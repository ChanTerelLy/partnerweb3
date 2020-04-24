from django.db import models
from beeline_parser.manager import NewDesign, Ticket
import re
from beeline_parser import system
import json
import datetime


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
        tickets = login.tickets()
        sw_tickets, sw_today = login.switched_tickets(tickets)
        print(sw_tickets)
        for ticket in sw_tickets:
            info_data = login.ticket_info(ticket.id)
            name, phone = cls.find_installer_in_text(info_data.comments)
            if name:
                try:
                    cls(full_name=name, number=phone).save()
                except Exception as e:
                    print(e)
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

    @classmethod
    def find_master(cls, number):
        master = Workers.objects.get(number=number).master
        return cls.objects.get(name=master)

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

