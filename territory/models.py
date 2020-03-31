from django.db import models
from tickets_handler.models import Workers, ChiefInstaller
# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=150)


class Area(models.Model):
    name = models.CharField(max_length=70)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    chief = models.ForeignKey(ChiefInstaller, on_delete=models.CASCADE)

# def get_p_house_id(street, house, building):
#     return NewDesign(os.getenv('SELL_CODE'),
#                      os.getenv('S_OPERATOR').encode('CP1251').decode('utf-8'),
#                      os.getenv('S_PASS')).get_id_by_fullname(street, house, building)

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

class PromoutingReport(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    date = models.DateField()
    agent = models.CharField(max_length=100)


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
