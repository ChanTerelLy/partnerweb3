from django.db import models

class Workers(models.Model):
    name = models.CharField(max_length=250, unique=True)
    number = models.CharField(max_length=50, unique=True)
    master = models.CharField(max_length=250)
    status = models.BooleanField()
    url = models.URLField()

    @classmethod
    def replace_num_worker(cls, tickets):
        if tickets is not None:
            for ticket in tickets:
                try:
                    worker = cls.objects.get(number=ticket.operator)
                    ticket.operator = worker.name
                except:
                    continue
            return tickets

    def __str__(self):
        return self.name