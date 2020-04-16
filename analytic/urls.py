from django.conf.urls import url
from .views import *
from django.contrib import admin

urlpatterns = [
    url(r'^load_moz/$', LoadMozFile.as_view(), name='promouting'),
]