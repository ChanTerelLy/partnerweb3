from django.shortcuts import render
from .models import AddressToDo as AddressToDoModel,Address, PromoutingReport as PromouteReportModel
from django.views.generic import ListView, FormView, TemplateView
from django.db.models import Q
from .forms import PromoutingReportFindForm, PromoutingReportForm
from datetime import datetime
from django.shortcuts import redirect
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
    ordering = ('date')

    def get_queryset(self):
        query = self.request.GET.get('q').split()
        if len(query) == 1:
            return PromouteReportModel.objects.filter(address__street__icontains=query[0]).order_by('-date')
        if len(query) == 2:
            return PromouteReportModel.objects.filter(Q(address__street__icontains=query[0])&Q(address__house__icontains=query[1])).order_by('-date')

class PromouteReportInsertForm(FormView):
    form_class = PromoutingReportForm
    template_name = 'territory/promoute_report_insert.html'

    def form_valid(self, form):
        str_addresses = form['addresses'].value()
        filter_addrs = list(filter(None, str_addresses.splitlines()))
        for addr in filter_addrs:
            addr_spl = addr.split()
            if len(addr_spl) == 2:
                addr_spl.append(None)
            addr_obj = Address.objects.filter(street=addr_spl[0], house=addr_spl[1], building=addr_spl[2]).first()
            report = PromouteReportModel(address=addr_obj, agent=form['agent'].value(), date=datetime.today())
            report.save()
        return redirect('promoute-report-insert')

class PromouteReportFindForm(FormView):
    form_class = PromoutingReportFindForm
    template_name = 'territory/promoute-report-find.html'

    def form_valid(self, form):
        street = form['street'].value().split()
        if len(street) == 1:
            return redirect(f'/promoute_report/?q={street[0]}')
        elif len(street) == 2:
            return redirect(f'/promoute_report/?q={street[0]}%20{street[1]}')

class PromouteReportTemplateView(TemplateView):
    template_name = 'territory/promoute-report-choose.html'


