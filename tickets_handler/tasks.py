from __future__ import absolute_import

import json

import jsonpickle

from partnerweb_project.celery import app as celery_app  # noqa
import os
from celery.schedules import crontab
from celery.task import periodic_task
from partnerweb_parser.date_func import dmYHM_to_datetime
from partnerweb_parser.manager import NewDesign
from django.apps import apps
from django.core.cache import cache
from datetime import datetime, timezone
from django.core.cache import cache
import pytz
tz = pytz.timezone('Europe/Moscow')
moscow_now = datetime.now(tz)


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
    FirebaseNotification = apps.get_model(app_label='tickets_handler', model_name='FirebaseNotification')
    tickets = cache.get('supervisors_tickets')
    devices = FCMDevice.objects.all()
    for device in devices:
        all_tickets = list([a for a in tickets['all_tickets'] if a.operator == device.device_id])
        call_today = NewDesign.call_today_tickets(all_tickets)
        if call_today:
            for ticket in call_today:
                notification = FirebaseNotification.objects.filter(ticket_number=ticket.ticket_paired_info.number).first()
                timer = dmYHM_to_datetime(ticket.ticket_paired_info.call_time)
                status = ticket.ticket_paired_info.status
                number = ticket.ticket_paired_info.number
                now = moscow.localize(datetime.now())
                expire = ((now - timer).total_seconds()//3600)
                if not notification:
                    FirebaseNotification(ticket_number=number,
                                         last_call_time=timer,
                                         last_ticket_status=status
                                         ).save()
                else:
                    diff_from_update = (now - notification.updated_at).total_seconds()//3600
                    if diff_from_update >= 4 and ((timer.hour == 0 and timer.minute == 0) \
                            or (expire >= 4)):
                            notification.today_count_notification += 1
                            notification.status = status
                            notification.last_call_time=timer
                            notification.save()
                    elif (timer.hour == datetime.now().hour and timer.day ==  datetime.now().day and diff_from_update > 1):
                        notification.today_count_notification += 1
                        notification.status = status
                        notification.last_call_time = timer
                        notification.save()
                    else:
                        continue
                device.send_message(title=f"Перезвон {ticket.ticket_paired_info.call_time}",
                                    click_action=f'https://partnerweb3.herokuapp.com/info/{ticket.id}',
                                    icon="https://partnerweb3.s3.amazonaws.com/static/image/favicon.ico",
                                    body=ticket.name)

#TODO:not working in parallel
@celery_app.task
def get_supervisor_tickets(login, password):
    AssignedTickets = apps.get_model(app_label='tickets_handler', model_name='AssignedTickets')
    auth = NewDesign('G800-37', login, password)
    assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
    switched_on_today, created_today_tickets, all_tickets = auth.three_month_tickets()
    cache.set(login.encode().decode('unicode-escape'), {'assigned_tickets': assigned_tickets,
                               'assigned_today': assigned_today,
                               'call_for_today': call_for_today,
                               'switched_on_tickets': switched_on_tickets,
                               'switched_on_today': switched_on_today,
                               'created_today_tickets': created_today_tickets,
                               'all_tickets': all_tickets,
                               'timestamp': moscow_now})
    for assigned in assigned_tickets:
        AssignedTickets.update(assigned, satelit_type=True)
    return [assigned_tickets,
            assigned_today,
            call_for_today,
            switched_on_tickets,
            switched_on_today,
            created_today_tickets,
            all_tickets]
