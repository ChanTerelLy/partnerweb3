from django.db import models
from tickets_handler.models import Workers, ChiefInstaller, AUP
from partnerweb_project.storage_backends import PublicMediaStorage
from django_resized import ResizedImageField
from django.conf import settings
# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=70)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    chief = models.ForeignKey(ChiefInstaller, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.city}  {self.name}'
class GlobalProblem(models.Model):
    text = models.TextField()

class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    street = models.CharField(max_length=70)
    house = models.CharField(max_length=5)
    building = models.CharField(max_length=5, null=True, blank=True)
    global_problems = models.ManyToManyField(GlobalProblem)
    entrance = models.IntegerField()
    floor = models.IntegerField()
    flats = models.IntegerField()
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    area_alias = models.CharField(max_length=250, null=True, blank=True)
    master = models.ManyToManyField(Workers)

    def __str__(self):
        return f'{self.street} {self.house} {self.building if self.building else ""}'




class Promouter(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)
    age = models.CharField(max_length=2)
    area = models.ManyToManyField(Area)
    date_hired = models.DateField(auto_now=True, blank=True)
    price_to_paper = models.IntegerField()
    bank_detail = models.CharField(max_length=30)
    master = models.ForeignKey(AUP, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} {self.id}'

class PromoutingReport(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    date = models.DateField()
    agent = models.CharField(max_length=100)

class EntranceImg(models.Model):
    img = ResizedImageField(storage=PublicMediaStorage())
    date_load = models.DateField(auto_now=True, blank=True)

class MailBoxImg(models.Model):
    img = ResizedImageField(storage=PublicMediaStorage())
    date_load = models.DateField(auto_now=True, blank=True)

class AddressToDo(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    to_promouter = models.ForeignKey(Promouter, on_delete=models.CASCADE)
    date_start = models.DateField(auto_now=True, blank=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.address}'

class AddressData(models.Model):
    promouter = models.ForeignKey(Promouter, on_delete=models.CASCADE)
    address = models.ForeignKey(AddressToDo, on_delete=models.CASCADE)
    date_start = models.DateField(auto_now=True, blank=True)
    entrance_img = models.ManyToManyField(EntranceImg)
    mailbox_img = models.ManyToManyField(MailBoxImg)

class PromouterPayments(models.Model):
    promouter = models.ForeignKey(Promouter, on_delete=models.CASCADE)
    sum  = models.IntegerField()

    def __str__(self):
        return f'{self.promouter.name} - {self.sum}'

