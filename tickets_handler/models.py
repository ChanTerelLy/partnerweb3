import uuid

from django.db import models
from partnerweb_parser.manager import NewDesign, Ticket
import re
from partnerweb_parser import system, mail, manager
import json
import datetime
from partnerweb_parser.date_func import dmYHM_to_datetime
from tickets_handler.tasks import update_date_for_assigned

class Modify(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Workers(models.Model):
    name = models.CharField(max_length=250, unique=True)
    number = models.CharField(max_length=50, unique=True)
    master = models.CharField(max_length=250)
    status = models.BooleanField()
    url = models.URLField()
    hiring_date = models.DateField(auto_now=True, blank=True)

    @classmethod
    @system.my_timer
    def replace_num_worker(cls, tickets):
        if tickets is not None:
            for ticket in tickets:
                try:
                    worker = cls.objects.get(number=ticket.operator)
                    ticket.name_operator = worker.name
                except:
                    continue
            return tickets

    def natural_key(self):
        return self.name

    @classmethod
    def update_workers(cls, auth):
        for worker in manager.Worker.get_workers(auth):
            operator = cls.objects.filter(number=worker.number)
            if not operator:
                cls(name=worker.name, number=worker.number, master=worker.master, status=worker.status,
                             url=worker.url).save()
                continue
            operator.update(name=worker.name, master=worker.master, status=worker.status, url=worker.url)


    def __str__(self):
        return self.name

class ChiefInstaller(models.Model):
    full_name = models.CharField(max_length=250, unique=True)
    number = models.CharField(max_length=50, unique=True)

class Installer(models.Model):
    full_name = models.CharField(max_length=250, unique=True)
    number = models.CharField(max_length=50, unique=True)

    @classmethod
    def parse_installers(cls, auth):
        login = NewDesign(auth['login'], auth['operator'], auth['password'])
        tickets = login.retrive_tickets()
        sw_tickets, sw_today = login.switched_tickets(tickets)
        for ticket in sw_tickets:
            info_data = login.ticket_info(ticket.id)
            name, phone = cls.find_installer_in_text(info_data.comments)
            try:
                installer, created = cls.objects.update_or_create(full_name=name)
                if not created:
                    installer.number = phone
                    installer.save()
                else:
                    cls(full_name=name, number=phone).save()
            except:
                continue

    @staticmethod
    def find_installer_in_text(comments):
        for comment in comments:
            data = re.search(r'Назначен Сервис - инженер (\w* \w* \w*), телефон (\d{11})', comment['text'])
            if (data):
                name = data.group(1)
                phone = data.group(2)
                return name, phone
        return None, None

    def __str__(self):
        return f'{self.full_name} {self.number}'




class AdditionalTicket(models.Model):
    number = models.IntegerField()
    positive = models.BooleanField()  # add or remove ticket
    operator = models.ForeignKey(Workers, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now=True)

    @classmethod
    def add(cls, payload):
        payload = json.loads(payload.decode('utf-8'))
        cls(number=payload['number'], positive=payload['positive'],
            operator=Workers.objects.get(number=int(payload['operator']))).save()

    @classmethod
    def show(cls, operator):
        AdditionalTicket.objects.filter(operator=Workers.objects.get(phone=operator))

    @classmethod
    def clear_switched_tickets(cls, sw_tickets, all_tickets):
        for t in cls.objects.filter(datetime__month=datetime.datetime.now().month):
            if t.positive:
                for all_t in all_tickets:
                    if isinstance(all_t.ticket_paired_info, Ticket):
                        if all_t.ticket_paired_info.number == t.number or all_t.number == t.number:
                            sw_tickets.append(all_t)
                            continue
            elif not t.positive:
                for sw_t in sw_tickets:
                    try:
                        if t.number == sw_t.ticket_paired_info.number or sw_t.number == t.number:
                            sw_tickets.remove(sw_t)
                            break
                    except:
                        continue
        return sw_tickets

    def __str__(self):
        return str(self.number)


class Employer(models.Model):
    profile_name = models.TextField()
    name = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    position = models.TextField()
    operator = models.ForeignKey(Workers, on_delete=models.CASCADE)
    operator_password = models.TextField()
    supervisor_password = models.CharField(max_length=50)

    @classmethod
    def find_master(cls, phone):
        master = Workers.objects.get(number=phone).master if Workers.objects.get(number=phone) else None
        master_obj = cls.objects.get(name=master) if master else cls.objects.none()
        return master_obj

    def __str__(self):
        return self.name


class Reminder(models.Model):
    ticket_number = models.TextField()
    client_name = models.TextField()
    client_number = models.CharField(max_length=10)
    timer = models.DateTimeField()
    operator = models.ForeignKey(Workers, on_delete=models.CASCADE)
    link = models.URLField(null=True, blank=True)
    recipient = models.TextField()


class TicketSource(models.Model):
    ticket_number = models.CharField(max_length=20, unique=True)
    source = models.CharField(max_length=50)
    agent = models.ForeignKey(Workers, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True, blank=True)

    @classmethod
    def add_source(cls, ticket_number, source, operator):
        try:
            data = cls.objects.get(ticket_number=ticket_number)
            data.source = source
            data.save()
        except:
            cls(ticket_number=ticket_number, source=source,
                agent=Workers.objects.get(number=operator)).save()

    @classmethod
    def find_source(cls, ticket_number):
        return cls.objects.get(ticket_number=ticket_number).source


class ACL(models.Model):
    code = models.CharField(max_length=50)
    date_end = models.DateField()

class AssignedTickets(models.Model):
    ticket_number = models.IntegerField()
    when_assigned = models.DateTimeField(null=True, blank=True)
    client_address = models.CharField(max_length=200)
    client_name = models.CharField(max_length=150)
    phones = models.CharField(max_length=150)
    assigned_date = models.DateTimeField()
    agent = models.ForeignKey(Workers, null=True, blank=True, on_delete=models.CASCADE)

    @classmethod
    def update(cls, ticket, *args, **kwargs):
        if(kwargs.get('satelit_type')):
            ticket = ticket.ticket_paired_info
        db_ticket = cls.objects.filter(ticket_number=ticket.number).first()
        if db_ticket:
            if ticket.assigned_date:
                db_ticket.when_assigned = dmYHM_to_datetime(ticket.assigned_date)
            db_ticket.client_address = ticket.address
            db_ticket.client_name = ticket.name
            db_ticket.phones = ticket.phones
            db_ticket.assigned_date = dmYHM_to_datetime(ticket.call_time)
            db_ticket.agent = Workers.objects.filter(number=ticket.operator).first()
            return db_ticket.save()
        else:
            assigned_date = dmYHM_to_datetime(ticket.call_time)
            agent = Workers.objects.filter(number=ticket.operator).first()
            result = cls(ticket_number=ticket.number,
                when_assigned=dmYHM_to_datetime(ticket.assigned_date) if ticket.assigned_date else None,
                client_address=ticket.address,
                phones=ticket.phones,
                assigned_date=assigned_date,
                agent=agent,
                client_name=ticket.name).save()
            db_ticket = ticket.__dict__
            db_ticket['mail_to'] = Employer.find_master(ticket.operator).email
            db_ticket['link'] = ''
            mail.EmailSender().agent_assign_ticket(db_ticket)

    def update_date(self):
        update_date_for_assigned()

class AUP(models.Model):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.IntegerField()

    def __str__(self):
        return f' {self.name} - {self.position}'

class FirebaseNotification(Modify):
    ticket_number = models.IntegerField()
    today_count_notification = models.IntegerField(default=0)
    last_call_time = models.DateTimeField(null=True, blank=True)
    last_ticket_status = models.CharField(max_length=255)
    worker = models.ForeignKey(Workers, on_delete=models.CASCADE, null=True, blank=True)