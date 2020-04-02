from django.db import models
from territory.models import Area, Address
from tickets_handler.models import Employer, Workers

class MOZSales(models.Model):
    ticket_number = models.IntegerField()
    creation_date = models.DateTimeField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    switched_date = models.DateField()
    tariff = models.CharField(max_length=250)
    moving = models.BooleanField()
    conv_segment = models.CharField(max_length=200)
    operator = models.ForeignKey(Workers, on_delete=models.CASCADE)

class Tariff:
    moz_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    conv_segment = models.CharField(max_length=200)
    extra_name = models.CharField(max_length=50)
