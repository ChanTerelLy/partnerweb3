from django.db.models import Count
from django.shortcuts import render
from django.views.generic import FormView
from .form import MozForm
from .models import MOZSales, Tariff
from django.http import JsonResponse
from django.shortcuts import render
from django.core import serializers
from tickets_handler.models import TicketSource, AssignedTickets
from territory.models import PromoutingReport
# Create your views here.

class LoadMozFile(FormView):
    form_class = MozForm
    template_name = 'analytic/load_moz.html'

    def form_valid(self, form):
        form['moz_file'].value()

def ticket_sourse_report(request):
    return render(request, 'analytic/ticket_source_report.html', {})

def ticket_source_data(request):
    dataset = TicketSource.objects.all()
    data = serializers.serialize('json', dataset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
    return JsonResponse(data, safe=False)

def assigned_report(request):
    return render(request, 'analytic/assigned_report.html', {})

def assigned_data(request):
    dataset = AssignedTickets.objects.all()
    data = serializers.serialize('json', dataset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
    return JsonResponse(data, safe=False)

def territory_report(request):
    return render(request, 'analytic/territory_report.html', {})

def territory_data(request):
    dataset = PromoutingReport.objects.all()
    data = serializers.serialize('json', dataset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
    return JsonResponse(data, safe=False)

