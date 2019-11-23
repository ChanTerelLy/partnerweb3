from django.conf.urls import url
from .views import *
from django.contrib import admin
urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^info/(?P<id>\d+)/$', ticket_info, name='ticket_info'),
    url('global_search/', global_search, name='global_search'),
    url('^tickets/', main_page, name='main_page_tickets'),
    url('admin/', admin.site.urls),
    url('update_worker/', update_workers, name='update_workers'),
    url('update_installers', update_installers, name='update_installers'),
    url(r'^info/(?P<ticket>\d+)/schedule/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', get_schedule_by_ticket_id, name='schedule'),
    url(r'^house_info/(?P<city_id>\d+)/(?P<house_id>\d+)/schedule/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', get_schedule_by_house_id, name='get_schedule_by_house_id'),
    url('street_search', street_search, name='street_search'),
    url('get_homes_by_street', get_homes_by_street, name='get_homes_by_street'),
    url('fast_house_search', fast_house_search, name='fast_house_search'),
    url('get_schedule_color', get_schedule_color, name='get_schedule_color'),
    url(r'house_info/(?P<city_id>\d+)/(?P<house_id>\d+)/$', house_info, name='house_info'),
    url(r'logout', logout, name='logout'),
    url(r'login_beeline/', redirect_auth, name='login_beeline'),
    url(r'personal_info/', get_personal_info, name='personal_info'),
    url('installers/', get_installers, name='installers'),
]