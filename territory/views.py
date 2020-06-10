from django.shortcuts import render
from .models import AddressToDo as AddressToDoModel,Address, \
    PromoutingReport as PromouteReportModel, Promouter, AddressData, EntranceImg, MailBoxImg
from django.views.generic import ListView, FormView, TemplateView, DetailView
from django.db.models import Q
from django.db import transaction
from .forms import PromoutingReportFindForm, PromoutingReportForm, AddressToDoForm
from datetime import datetime
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
# Create your views here.

def promouter_address_to_do(request, id):
    promouter = Promouter.objects.filter(id=id).first()
    addr_to_do = AddressToDoModel.objects.filter(to_promouter=promouter, done=False)
    return render(request, 'territory/promouter_addresses_to_do.html', {'addr_to_do': addr_to_do})

def promouter_images(request, id):
    promouter = Promouter.objects.filter(id=id).first()
    address_data = AddressData.objects.filter(address__done=True, promouter=promouter)
    return render(request, 'territory/promouter_images.html',  {'address_data': address_data})

def load_image(request):
    if request.method == 'POST':
            imgs = request.FILES
            promouter_id = request.POST.get('promouter_id')
            address_id = request.POST.get('address_id')
            type = request.POST.get('type')
            address_todo = AddressToDoModel.objects.get(id=address_id)
            address, address_exist_before = AddressData.objects.get_or_create(promouter=Promouter.objects.get(id=promouter_id),
                                                 address=address_todo)
            if (type == 'mailbox'):
                for i in imgs:
                    img = MailBoxImg.objects.create(img=request.FILES[i])
                    address.mailbox_img.add(img)
            if (type == 'entrancebox'):
                for i in imgs:
                    img = EntranceImg.objects.create(img=request.FILES[i])
                    address.entrance_img.add(img)
            address_todo.done = True
            address_todo.save()
    return JsonResponse({'status': 'ok'})

class PromouterListView(ListView):
    model = Promouter
    template_name = 'territory/promouter_list_view.html'
    context_object_name = 'promouters'



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
            return PromouteReportModel.objects.filter(Q(address__street__icontains=query[0])&
                                                      Q(address__house__icontains=query[1])).order_by('-date')

@method_decorator(transaction.atomic, name='dispatch')
class PromouteReportInsertForm(FormView):
    form_class = PromoutingReportForm
    template_name = 'territory/promoute_report_insert.html'

    def form_valid(self, form):
        str_addresses = form['addresses'].value()
        filter_addrs = list(filter(None, str_addresses.splitlines()))
        for addr in filter_addrs:
            import re
            match = re.search(r"(.+)\t(\d+)\t(\d*)", addr)
            building = None
            try:
                building = match.group(3) if match.group(3) else None
            except Exception as e:
                print(e)
            date = form['date'] if form['date'] else datetime.today()
            addr_obj = Address.objects.filter(street=match.group(1), house=match.group(2),
                                              building=building).first()
            report = PromouteReportModel(address=addr_obj, agent=form['agent'].value(), date=date.value())
            if form['assign_to_promouter'].value():
                promouter_id = form['promouter_choice'].value()
                assign_to_promouter = AddressToDoModel(address=addr_obj, to_promouter=Promouter.objects.get(id=promouter_id))
                assign_to_promouter.save()
            report.save()
        return redirect('promoute-report-insert')

    @method_decorator(transaction.atomic)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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


