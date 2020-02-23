from django.db import models
from tickets_handler.beeline_parser.manager import NewDesign
import re
from tickets_handler.beeline_parser import system
import os
import json
from PIL import Image
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
            print(name)
            print(phone)
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

    # is it work?)
    @classmethod
    def check_visability(cls, operator, tickets):
        ad_tickets = cls.objects.get(who_add=operator)
        if ad_tickets:
            clear_tickets = []
            for ticket in tickets:
                try:
                    cls.objects.get(number=ticket.number)
                    continue
                except:
                    clear_tickets.append(ticket)
        else:
            return False

    @classmethod
    def add(cls, payload):
        payload = json.loads(payload.decode('utf-8'))
        cls(number=payload['number'], positive=payload['positive'],
            operator=Workers.objects.get(number=int(payload['operator']))).save()

    @classmethod
    def show(cls, operator):
        AdditionalTicket.objects.filter(operator=Workers.objects.get(phone=operator))


class TicketPrice(models.Model):
    ticket_number = models.IntegerField()
    price = models.IntegerField()
    ratio = models.IntegerField()

    @classmethod
    def set_price(cls, ticket_number, price, ratio=1):
        cls(ticket_number, price, ratio).save()

    @classmethod
    def get_price(cls, ticket_number):
        ticket = cls.objects.get(ticket_number)
        return ticket.price


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


class Area(models.Model):
    name = models.CharField(max_length=70)
    city = models.CharField(max_length=20)


def get_p_house_id(street, house, building):
    return NewDesign(os.getenv('SELL_CODE'),
                     os.getenv('S_OPERATOR').encode('CP1251').decode('utf-8'),
                     os.getenv('S_PASS')).get_id_by_fullname(street, house, building)


class Address(models.Model):
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=70)
    house = models.CharField(max_length=5)
    building = models.CharField(max_length=5)
    category = models.CharField(max_length=20, default=None)  # red, yellow and etc
    entrance = models.IntegerField(default=None)
    floor = models.IntegerField()
    flats = models.IntegerField()
    # p_link = models.URLField()  # partnerweb link
    # p_house_id = models.IntegerField(default=get_p_house_id(street, house, building))

    def __str__(self):
        return f'{self.street} {self.house} {self.building}'


class Promouter(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)
    age = models.CharField(max_length=2)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    date_hired = models.DateField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class EntranceImg(models.Model):
    img = models.ImageField()
    date_load = models.DateField(auto_now=True, blank=True)

class MailBoxImg(models.Model):
    img = models.ImageField()
    date_load = models.DateField(auto_now=True, blank=True)

class AddressToDo(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    to_promouter = models.ForeignKey(Promouter, on_delete=models.CASCADE)
    date_start = models.DateField(auto_now=True, blank=True)
    done = models.BooleanField(default=False)

class AddressData(models.Model):
    promouter = models.ForeignKey(Promouter, on_delete=models.CASCADE)
    address = models.ForeignKey(AddressToDo, on_delete=models.CASCADE)
    date_start = models.DateField(auto_now=True, blank=True)
    entrance_img = models.ManyToManyField(EntranceImg)
    mailbox_img = models.ManyToManyField(MailBoxImg)


# if __name__ == '__main__':
#     homenko = Installer.parse_installers({'login': os.getenv('SELL_CODE'), 'operator': os.getenv('S_OPERATOR'),
#                                           'password': os.getenv('S_PASSWORD')})
