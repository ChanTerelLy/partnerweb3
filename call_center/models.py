from django.db import models

# Create your models here.


class Subscribers(models.Model):
    called = models.BooleanField()
    name = models.TextField()
    phone = models.TextField()
    address = models.TextField()
    city = models.TextField()
    extra = models.TextField()
    status_result = models.TextField()
    call_time = models.TextField()