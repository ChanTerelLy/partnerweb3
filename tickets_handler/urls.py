from django.conf.urls import url
from .views import *
from django.contrib import admin
urlpatterns = [
    url(r'^login_beeline/$', auth, name='login_beeline'),
    url(r'^info/(?P<id>\d+)/$', ticket_info, name='ticket_info'),
    url('global_search/', global_search, name='global_search'),
    url('^tickets/', main_page, name='main_page_tickets'),
    url('^telegram_news/', telegram_news, name='telegram_news'),
    url('admin/', admin.site.urls),
    url('update_worker/', update_workers, name='update_workers'),
    url('test_page', test_page, name='test_page'),
    url('update_installers', update_installers, name='update_installers'),
    url(r'^info/(?P<ticket>\d+)/schedule/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', get_schedule, name='schedule'),
    url('street_search', street_search, name='street_search'),
    url('fast_house_search', fast_house_search, name='fast_house_search'),
    # url('', redirect_auth, name='redirect_auth'),
]