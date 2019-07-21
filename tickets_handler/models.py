from django.db import models


class Auth(models.Model):
    sell_code = models.CharField(max_length=255)
    operator = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class DateTime(models.Model):
    datetime = models.CharField(max_length=2550)
    comments = models.CharField(max_length=2550)
    status = models.CharField(max_length=255)
