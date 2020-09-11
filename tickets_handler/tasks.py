from __future__ import absolute_import

import jsonpickle

from partnerweb_project.celery import app as celery_app  # noqa
import os
from celery.schedules import crontab
from celery.task import periodic_task
from partnerweb_parser.date_func import dmYHM_to_datetime
from partnerweb_parser.manager import NewDesign
from django.apps import apps
from django.core.cache import cache
from datetime import datetime
from django.core.cache import cache


@celery_app.task
def update_date_for_assigned():
    auth = NewDesign(os.getenv('SELL_CODE'),os.getenv('S_OPERATOR'),os.getenv('S_PASS'))
    AssignedTickets = apps.get_model(app_label='tickets_handler', model_name='AssignedTickets')
    db_tickets = AssignedTickets.objects.filter(when_assigned=None)
    ticket_with_id = ''
    for ticket in db_tickets:
        supervisors_tickets = cache.get('supervisors_tickets')
        for sp_ticket in supervisors_tickets['all_tickets']:
                if hasattr(sp_ticket.ticket_paired_info, 'number') and sp_ticket.ticket_paired_info.number == ticket.ticket_number:
                    ticket_with_id = sp_ticket
        if not ticket_with_id:
            continue
        ticket_info = auth.ticket_info(ticket_with_id.ticket_paired_info.id)
        ticket.when_assigned = dmYHM_to_datetime(ticket_info.assigned_date) if ticket_info.assigned_date else None
        ticket.save()

@celery_app.task
def update_workers(auth):
    Workers = apps.get_model(app_label='tickets_handler', model_name='Workers')
    Workers.update_workers(auth)

@celery_app.task
def notify_call_timer():
    FCMDevice = apps.get_model(app_label='fcm_django', model_name='FCMDevice')
    tickets = cache.get('supervisors_tickets')
    devices = FCMDevice.objects.all()
    for device in devices:
        all_tickets = list([a for a in tickets['all_tickets'] if a.operator == device.device_id])
        call_today = NewDesign.call_today_tickets(all_tickets)
        if call_today:
            for ticket in call_today:
                device.send_message(title="Перезвон",
                                    click_action=f'https://partnerweb3.herokuapp.com/info/{ticket.id}',
                                    icon="https://partnerweb3.s3.amazonaws.com/static/image/favicon.ico",
                                    body=ticket.number)
