from django.conf.urls import url
from .views import *
from django.contrib import admin

urlpatterns = [
    url(r'^promouting/$', AddressToDo.as_view(), name='promouting'),
]