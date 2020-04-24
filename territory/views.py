from django.shortcuts import render
from .models import AddressToDo as AddressToDoModel, PromoutingReport as PromouteReportModel
from django.views.generic import ListView
# Create your views here.
class AddressToDo(ListView):
    model = AddressToDoModel
    template_name = 'beeline_html/address_to_do.html'
    context_object_name = 'addresses'

def send_image_todo_addresses(request):
    if request.is_ajax():
        if request.method == "POST":
            pass

class PromouteReport(ListView):
    model = PromouteReportModel
    template_name = 'territory/promoute_report.html'
    context_object_name = 'addresses'
    queryset = PromouteReportModel.objects.all().order_by('-date')
    paginate_by = 100
