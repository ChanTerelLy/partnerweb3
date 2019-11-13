from django.db import models
from tickets_handler.models import Workers
class MonthReport(models.Model):
    name = models.ForeignKey(Workers, on_delete=models.CASCADE)
    month = models.DateField()
    week = models.DateField()
    switch = models.IntegerField()
    assign = models.IntegerField()
    created = models.IntegerField()




