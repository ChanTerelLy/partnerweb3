from django.conf.urls import url

from tickets_handler.json_views import *
from tickets_handler.template_views import HouseSearch, CheckNumber, Index, IsmSchedule, CheckCTN
from .views import *
from django.contrib import admin

urlpatterns = [
    url('admin/', admin.site.urls),

    #Pages URLs
    url(r'^login/$', login, name='login'),
    url(r'^info/(?P<id>\d+)/$', ticket_info, name='ticket_info'),
    url('global_search/', global_search, name='global_search'),
    url('^tickets/', main_page, name='main_page_tickets'),
    url(r'^feedback/$', feedback, name='feedback'),
    url(r'^get_ctn_info/$', get_ctn_info, name='get_ctn_info'),
    url(r'logout', logout, name='logout'),
    url(r'login_beeline/', redirect_auth, name='login_beeline'),
    url('installers/', get_installers, name='installers'),

    # Template URLs
    url('house_search', HouseSearch.as_view(), name='house_search'),
    url('check_number/', CheckNumber.as_view(), name='check_number'),
    url(r'^index/$', Index.as_view(), name='index'),
    url(r'^ism_schedule/$', IsmSchedule.as_view(), name='ism_schedule'),
    url(r'^check_ctn/$', CheckCTN.as_view(), name='check_ctn'),

    #Ajax URLs
    url(r'^assigned_tickets/$', get_assigned_tickets, name='assigned_tickets'),
    url(r'^call_today_tickets/$', get_call_today_tickets, name='call_today_tickets'),
    url(r'^switched_tickets/$', get_switched_tickets, name='switched_tickets'),
    url(r'^count_created_today/$', get_count_created_today, name='count_created_today'),
    url(r'^ticket_source/$', source_tickets, name='source_tickets'),
    url(r'^change_phone_number/$', change_phone_number, name='change_phone_number'),
    url(r'delete_ticket/(?P<ticket>\d+)/', delete_additional_ticket, name='delete_ticket'),
    url(r'^ticket_info/(?P<id>\d+)/$', ticket_info_json, name='ticket_info_json'),
    url(r'^info/(?P<ticket>\d+)/schedule/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', get_schedule_by_ticket_id,
        name='schedule'),
    url(r'^send_mail/$', send_mail, name='send_mail'),
    url(r'^add_additional_ticket/$', add_additional_ticket, name='add_additional_ticket'),
    url(r'personal_info/', get_personal_info, name='personal_info'),

    #UpdateModels URLs
    url('update_workers/', update_workers, name='update_workers'),
    url('update_installers', update_installers, name='update_installers'),

    #PresetSystem URLs
    url(r'^get_mobile_presets/$', get_mobile_presets_json, name='get_mobile_presets_json'),
    url(r'^get_presets/$', get_presets_json, name='get_presets_json'),

    #StreetSystem URLs
    url(r'^house_info/(?P<city_id>\d+)/(?P<house_id>\d+)/schedule/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$',
        get_schedule_by_house_id, name='get_schedule_by_house_id'),
    url('street_search', street_search, name='street_search'),
    url('get_homes_by_street', get_homes_by_street, name='get_homes_by_street'),
    url('get_schedule_color', get_schedule_color, name='get_schedule_color'),
    url(r'house_info/(?P<city_id>\d+)/(?P<house_id>\d+)/$', house_info, name='house_info'),
    url(r'house_info/(?P<city_id>\d+)/(?P<house_id>\d+)/(?P<flat>\d+)$', check_fraud, name='check_fraud'),
    url(r'^promouting/$', AddressToDo.as_view(), name='promouting'),
]
