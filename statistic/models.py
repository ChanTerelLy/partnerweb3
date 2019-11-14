from django.db import models
from tickets_handler.models import Workers
from tickets_handler.beeline_parser import manager, date_func

class Services(models.Model):
    IS_INAC_PRESET_id = models.CharField(max_length=100, blank=True, null=True)
    IS_INAC_PRESET_name = models.CharField(max_length=250, blank=True, null=True)
    IS_PRESET_id = models.CharField(max_length=100, blank=True, null=True)
    IS_PRESET_name = models.CharField(max_length=250, blank=True, null=True)
    VPDN_id = models.CharField(max_length=100, blank=True, null=True)
    VPDN_name = models.CharField(max_length=250, blank=True, null=True)
    IPTV_id = models.CharField(max_length=100, blank=True, null=True)
    IPTV_name = models.CharField(max_length=250, blank=True, null=True)
    TVE_id = models.CharField(max_length=100, blank=True, null=True)
    TVE_name = models.CharField(max_length=250, blank=True, null=True)
    W_NONSTOP_id = models.CharField(max_length=100, blank=True, null=True)
    W_NONSTOP_name = models.CharField(max_length=250, blank=True, null=True)

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.PositiveIntegerField(unique=True)
    ticket_paired = models.PositiveIntegerField()
    address_id = models.PositiveIntegerField(unique=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    operator = models.ForeignKey(Workers, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)

class MonthReport(models.Model):
    name = models.ForeignKey(Workers, on_delete=models.CASCADE)
    month = models.DateField()
    week = models.DateField()
    switch = models.IntegerField()
    assign = models.IntegerField()
    created = models.IntegerField()

    @staticmethod
    def parse_statistic(auth, pages=150, dateFrom=False, dateTo=False):
        tickets = auth.tickets(pages=pages, dateFrom=dateFrom, dateTo=dateTo)
        for ticket in tickets:
            ticket = auth.ticket_info(ticket.id)
            if ticket.services:
                s = Services(IS_INAC_PRESET_id=str(ticket.services.IS_INAC_PRESET_id),
                         IS_INAC_PRESET_name=str(ticket.services.IS_INAC_PRESET_name),
                         IS_PRESET_id=str(ticket.services.IS_PRESET_id),
                         IS_PRESET_name=str(ticket.services.IS_PRESET_name),
                         VPDN_id=str(ticket.services.VPDN_id),
                         VPDN_name=str(ticket.services.VPDN_name),
                         IPTV_id=str(ticket.services.IPTV_id),
                         IPTV_name=str(ticket.services.IPTV_name),
                         TVE_id=str(ticket.services.TVE_id),
                         TVE_name=str(ticket.services.TVE_name),
                         W_NONSTOP_id=str(ticket.services.W_NONSTOP_id),
                             W_NONSTOP_name=str(ticket.services.W_NONSTOP_name))
                s.save()
                try:
                    Ticket(ticket.id, ticket.number, ticket.ticket_paired, ticket.address_id, ticket.status.split()[0],
                           date_func.dmYHM_to_date(ticket.call_time), Workers.objects.get(number=ticket.operator).id,
                           s.id).save()
                except Exception as e:
                    print(e)
                    continue
            else:
                try:
                    Ticket(ticket.id, ticket.number, ticket.ticket_paired, ticket.address_id, ticket.status.split()[0],
                           date_func.dmYHM_to_date(ticket.call_time), Workers.objects.get(number=ticket.operator).id,
                           '').save()
                except Exception as e:
                    print(e)
                    continue
