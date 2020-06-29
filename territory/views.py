from django.shortcuts import render
from .models import AddressToDo as AddressToDoModel,Address, \
    PromoutingReport as PromouteReportModel, Promouter, AddressData, EntranceImg, MailBoxImg, PromouterPayments
from django.views.generic import ListView, FormView, TemplateView, DetailView
from django.db.models import Q, Sum
from django.db import transaction
from .forms import PromoutingReportFindForm, PromoutingReportForm, AddressToDoForm
from datetime import datetime
from django.shortcuts import redirect, resolve_url, reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from partnerweb_parser.mail import EmailSender
import traceback
# Create your views here.

def promouter_address_to_do(request, id):
    promouter = Promouter.objects.filter(id=id).first()
    addr_to_do = AddressToDoModel.objects.filter(to_promouter=promouter, done=False)
    return render(request, 'territory/promouter_addresses_to_do.html', {'addr_to_do': addr_to_do})

def promouter_images(request, id):
    promouter = Promouter.objects.filter(id=id).first()
    promouter_price = promouter.price_to_paper
    address_data = AddressData.objects.filter(address__done=True, promouter=promouter)
    sum_to_pay = 0
    for address in address_data:
        ad = address.address.address
        sum_to_pay += (promouter.price_to_paper/ 100) * \
        (address.mailbox_img.count() / ad.entrance) * ad.flats
    promouter_payment = PromouterPayments.objects.filter(promouter=promouter).aggregate(Sum('sum'))
    recieved_payment = promouter_payment['sum__sum'] if promouter_payment['sum__sum'] else 0
    payment_left = int(sum_to_pay - recieved_payment)
    payments = {
        'total': int(sum_to_pay),
        'recieved': recieved_payment,
        'left': payment_left,
        'promouter_price': promouter_price,
        'card' : promouter.bank_detail
    }
    return render(request, 'territory/promouter_images.html',  {'address_data': address_data,
                                                                'payments' : payments
                                                                })

def load_image(request):
    try:
        if request.method == 'POST':
                imgs = request.FILES
                for i in imgs:
                    image = request.FILES[i].name
                    if MailBoxImg.objects.filter(img=image):
                        return JsonResponse({'status': 'error', 'description': f'Фотография {image} '
                                                                               f'уже существует в системе'})
                promouter_id = request.POST.get('promouter_id')
                promouter = Promouter.objects.get(id=promouter_id)
                address_id = request.POST.get('address_id')
                type = request.POST.get('type')
                address_todo = AddressToDoModel.objects.get(id=address_id)
                address, address_exist_before = AddressData.objects.get_or_create(promouter=promouter,
                                                     address=address_todo)
                email_text = {'promouter': promouter.name,
                              'address': address.address.address,
                              'photo_count': len(imgs),
                              'mail_to' : promouter.master.email,
                              'images_link' : request.build_absolute_uri(reverse('promouter_images',  kwargs={'id': promouter_id}))}
                if (type == 'mailbox'):
                    if len(imgs) + address.mailbox_img.count() <= address.address.address.entrance:
                        for i in imgs:
                            img = MailBoxImg.objects.create(img=request.FILES[i])
                            address.mailbox_img.add(img)
                        EmailSender().promouter_upload_imagebox(email_text)
                    else:
                        return JsonResponse({'status': 'error', 'description': f'Фотографий не может быть больше чем подъездов,'
                                                                               f'уже загружено в системе {address.mailbox_img.count()}'})

                if (type == 'entrancebox'):
                    if len(imgs) + address.entrance_img.count() <= address.address.address.entrance:
                        for i in imgs:
                            img = EntranceImg.objects.create(img=request.FILES[i])
                            address.entrance_img.add(img)
                    else:
                        return JsonResponse(
                            {'status': 'error', 'description': f'Фотографий не может быть больше чем подъездов,'
                                                                                   f'уже загружено в системе {address.mailbox_img.count()}'})
                address_todo.done = True
                address_todo.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        text = f'{e} \n {traceback.format_exc()}'
        EmailSender().error_mail(text)

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


