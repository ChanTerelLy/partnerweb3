from django.db import models
class Exam(models.Model):
    one = models.CharField(max_length=255),
    two = models.CharField(max_length=255),
    three = models.CharField(max_length=255)
# Create your models here.
