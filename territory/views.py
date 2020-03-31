from django.shortcuts import render
from .models import AddressToDo as AddressToDoModel
from django.views.generic import ListView
# Create your views here.
class AddressToDo(ListView):
    model = AddressToDoModel
    template_name = 'beeline_html/address_to_do.html'
    context_object_name = 'addresses'
