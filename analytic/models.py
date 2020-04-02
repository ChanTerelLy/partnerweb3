from django.db import models

# Create your models here.
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


