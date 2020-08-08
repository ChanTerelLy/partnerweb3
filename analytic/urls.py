from django.conf.urls import url
from .views import *
from django.contrib import admin

urlpatterns = [
    url(r'^load_moz/$', LoadMozFile.as_view(), name='promouting'),
    url(r'^ticket_source_report/$', ticket_sourse_report, name='ticket_source_report'),
    url(r'^ticket_source_data/$', ticket_source_data, name='ticket_source_data'),
    url(r'^assigned_report/$', assigned_report, name='assigned_report'),
    url(r'^assigned_data/$', assigned_data, name='assigned_data'),
    url(r'^territory_report/$', territory_report, name='territory_report'),
    url(r'^territory_data/$', territory_data, name='territory_data'),
]