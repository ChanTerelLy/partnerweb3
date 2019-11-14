from django.conf.urls import url
from .views import *

urlpatterns = [
    url('parse_ticket_by_year/', parse_statistic, name='parse_ticket_by_year')
]