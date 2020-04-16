from django.shortcuts import render
from django.views.generic import FormView
from .form import MozForm
from .models import MOZSales, Tariff
# Create your views here.

class LoadMozFile(FormView):
    form_class = MozForm
    template_name = 'analytic/load_moz.html'

    def form_valid(self, form):
        form['moz_file'].value()