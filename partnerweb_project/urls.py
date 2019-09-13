from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('tickets_handler.urls'))
]