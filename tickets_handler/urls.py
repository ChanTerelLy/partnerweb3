from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^login_beeline/$', auth, name='login_beeline'),
    url(r'^info/(?P<id>\d+)/$', ticket_info, name='ticket_info'),
    url('global_search/', global_search, name='global_search'),
    url('^tickets/', main_page, name='main_page_tickets'),
    url(r'^telegram_news/', telegram_news, name='telegram_news')
]