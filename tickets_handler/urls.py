from django.conf.urls import url
from .views import *
from django.contrib import admin
urlpatterns = [
    url(r'^login_beeline/$', auth, name='login_beeline'),
    url(r'^info/(?P<id>\d+)/$', ticket_info, name='ticket_info'),
    url('global_search/', global_search, name='global_search'),
    url('^tickets/', main_page, name='main_page_tickets'),
    url(r'^telegram_news/', telegram_news, name='telegram_news'),
    url('admin/', admin.site.urls),
    url('update_worker/', update_workers, name='update_workers'),
    url('test_page', test_page, name='test_page')
    #url('', redirect_auth, name='redirect_auth'),
]