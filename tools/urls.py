from django.conf.urls import url
from .views import *
from django.contrib import admin

urlpatterns = [
    url('partnerweb3_mobile/', Partnerweb3MobileLending.as_view(), name='partnerweb3_mobile_lending'),
]
