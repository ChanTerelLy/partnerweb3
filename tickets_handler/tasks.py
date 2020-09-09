from __future__ import absolute_import
from partnerweb_project.celery import app as celery_app  # noqa
import os
from celery.schedules import crontab
from celery.task import periodic_task
from partnerweb_parser.date_func import dmYHM_to_datetime
from partnerweb_parser.manager import NewDesign
from django.apps import apps
from django.core.cache import cache


@periodic_task(run_every=(crontab(hour='*/12')), name="update_date_for_assigned")
def update_date_for_assigned():
    auth = NewDesign(os.getenv('SELL_CODE'),os.getenv('S_OPERATOR'),os.getenv('S_PASS'))
    AssignedTickets = apps.get_model(app_label='tickets_handler', model_name='AssignedTickets')
    db_tickets = AssignedTickets.objects.filter(when_assigned=None)
    ticket_with_id = ''
    for ticket in db_tickets:
        logger.info("Sent feedback email")
        supervisors_tickets = cache.get('supervisors_tickets')
        for sp_ticket in supervisors_tickets['all_tickets']:
                if hasattr(sp_ticket.ticket_paired_info, 'number') and sp_ticket.ticket_paired_info.number == ticket.ticket_number:
                    ticket_with_id = sp_ticket
        ticket_info = auth.ticket_info(ticket_with_id.ticket_paired_info.id)
        ticket.when_assigned = dmYHM_to_datetime(ticket_info.assigned_date) if ticket_info.assigned_date else None
        ticket.save()