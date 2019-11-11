from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from tickets_handler import views

urlpatterns = [
    path('', include('tickets_handler.urls')),
    url(r'^$', views.redirect_auth, name='redirect_auth'),
]