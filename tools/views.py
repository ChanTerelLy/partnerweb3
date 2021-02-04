from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
from .models import *


class Partnerweb3MobileLending(ListView):
    template_name = 'tools/partnerweb3_mobile_lending.html'
    model = Partnerweb3Mobile
    context_object_name = 'releases'
