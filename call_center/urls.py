from django.conf.urls import url
from .views import *
from django.contrib import admin

urlpatterns = [
    url(r'^get_subscriber/$', get_subscriber, name='get_subscriber'),
    url(r'^set_subscriber/$', set_subscriber, name='set_subscriber'),
    ]