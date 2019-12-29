from tickets_handler.beeline_parser.manager import NewDesign, OldDesign, Worker, Auth
from django.shortcuts import render, redirect
from .form import AuthForm, DateTimeForm, CreateTicketForm
from .models import Workers as WorkersModel, Installer, AdditionalTicket, TicketPrice
from django.http import HttpResponse, JsonResponse
from tickets_handler.beeline_parser import system
from django.contrib import messages
import grequests
import json
from django.core import serializers

@system.my_timer
def main_page(request):
    code, operator, password = request.session['sell_code'], request.session['operator'], request.session['password']
    if Auth(code, operator, password).auth_response_status:
        auth = NewDesign(code, operator, password)
        all_assigned_tickets, all_assigned_today, all_call_for_today, all_switched_on_tickets,\
        all_switched_on_today, all_created_today_tickets = [],0,[],[],0,0
        assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
        switched_on_today, created_today_tickets = auth.three_month_tickets()
        all_assigned_tickets.extend(assigned_tickets)
        all_call_for_today.extend(call_for_today)
        all_switched_on_tickets.extend(switched_on_tickets)
        all_assigned_today += assigned_today
        all_switched_on_today += switched_on_today
        all_created_today_tickets += created_today_tickets
        return render(request, 'beeline_html/main_page_tickets.html',
                      {'assigned_tickets': WorkersModel.replace_num_worker(all_assigned_tickets),
                       'call_for_today': WorkersModel.replace_num_worker(all_call_for_today),
                       'switched_on_tickets': WorkersModel.replace_num_worker(all_switched_on_tickets),
                       'assigned_today': all_assigned_today, 'switched_on_today': all_switched_on_today,
                       'created_today_tickets': all_created_today_tickets})
    else:
        messages.error(request, f'Ошибка Аутентификации, неправильный логин или пароль!')
        request.session['sell_code'], request.session['operator'], request.session['password'] = '','',''
        return redirect('login')

@system.my_timer
def global_search(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    tickets = auth.global_search()
    return render(request, 'beeline_html/global_search.html', {'tickets':tickets})

def ticket_info(request, id):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    ticket_info = auth.ticket_info(id)
    dateform = DateTimeForm(request.POST)
    gp_houses = auth.get_gp_ticket_search(id)
    if request.method == 'POST':
        auth.change_ticket(id, dateform['datetime'].value(),dateform['comments'].value(), dateform['status'].value())
        return redirect('ticket_info', id)
    return render(request,'beeline_html/ticket_info.html', {'ticket_info':ticket_info, 'form': dateform,
                                                            'gp_houses': gp_houses})
def ticket_info_json(request, id):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    ticket = auth.ticket_info(id).__dict__
    return JsonResponse(ticket, safe=False)

def login(request):
    form = AuthForm(request.POST)
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if 'NewDesign' in request.POST:
            request.session['Design'] = 'NewDesign'
        elif 'OldDesign' in request.POST:
            request.session['Design'] = 'OldDesign'
        request.session['sell_code'], request.session['operator'],request.session['password'] = form['sell_code'].value(), form['operator'].value(), form['password'].value()
        if form.is_valid():
            return redirect('main_page_tickets')
    return render(request, 'beeline_html/login_beeline.html', {'form': form})

def redirect_auth(request):
    return redirect('login')

def update_workers(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    for worker in Worker.get_workers(auth):
        try:
            WorkersModel(name=worker.name, number=worker.number, master=worker.master, status=worker.status,
                                        url=worker.url).save()
        except:
            continue
    return HttpResponse(
        'Done'
    )

def update_installers(request):
    Installer.parse_installers({'login': request.session['sell_code'], 'operator': request.session['operator'],
                                'password': request.session['password']})
    return HttpResponse('Done')

def get_installers(request):
    installers = Installer.objects.all()
    return render(request, 'beeline_html/installers.html', {'installers' : installers})

def street_search(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    input = request.GET.get('streetPattern', '')
    return JsonResponse(auth.street_search_type(input), safe=False)

def get_homes_by_street(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    street_id = request.GET.get('street_id', '')
    data = auth.get_houses_by_street(auth.get_homes(street_id))
    return JsonResponse(data, safe=False)

def fast_house_search(request):
    return render(request, 'beeline_html/fast_house_search.html')

def get_schedule_color(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    house_id = request.GET.get('house_id', '')
    ticket_id = request.GET.get('ticket_id', '')
    return JsonResponse(auth.month_schedule_color(house_id, ticket_id), safe=False)

def house_info(request, city_id, house_id):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    gp_houses, areas = auth.get_gp_by_house_id(house_id)
    house_full_name = auth.get_full_house_info(house_id)['house_address']
    p_form = CreateTicketForm()
    gp = areas + gp_houses
    if request.method == 'POST':
        p_form = CreateTicketForm(request.POST)
        bundel_id, service_type, vpdn = p_form['basket'].value().split(';')
        create_ticket_form = auth.create_ticket(house_id, p_form['flat'].value(), p_form['client_name'].value(),
                                                p_form['client_patrony'].value(), p_form['client_surname'].value(),
                                                p_form['phone_number_1'].value(), bundel_id ,service_type, vpdn)
        return redirect('ticket_info', create_ticket_form['data']['ticket_id'])
    return render(request, 'beeline_html/house_info.html', {'gp_houses' : gp, 'name': house_full_name,
                                                            'p_form' : p_form})
def get_mobile_presets_json(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    city_id, house_id = request.GET.get('city_id'), request.GET.get('house_id')
    data = auth.get_mobile_presets(city_id, house_id)
    presets = auth.parse_preset(data)
    return JsonResponse(presets , safe=False)

def get_presets_json(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    city_id, house_id = request.GET.get('city_id'), request.GET.get('house_id')
    data = auth.get_presets(city_id, house_id)
    presets = auth.parse_preset(data)
    return JsonResponse(presets, safe=False)


def get_schedule_by_ticket_id(request, ticket, year, month, day):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    return JsonResponse(auth.schedule_interval_by_day(ticket, year, month, day, house_id=False), safe=False)

def get_schedule_by_house_id(request, city_id, house_id, year, month, day):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    return JsonResponse(auth.schedule_interval_by_day(ticket_id=False, year=year, month=month, day=day, house_id=house_id), safe=False)

def logout(request):
    request.session['sell_code'], request.session['operator'], request.session['password'] = '', '',''
    return redirect('login')

def get_personal_info(request):
    phone = request.GET.get('phone')
    city = request.GET.get('city')
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    return JsonResponse(auth.get_personal_info(phone, city), safe=False)

def check_number(request):
    return render(request, 'beeline_html/check_number.html')

def check_fraud(request, city_id, house_id, flat):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    res_data = auth.check_fraud(house_id, flat)
    if res_data['data']:
        return JsonResponse({'result': 'Можно создавать заявку'})
    else:
        return JsonResponse({'result': res_data['metadata']['message']})

def delete_ticket(request, ticket):
    operator = WorkersModel.objects.get(number=request.session['operator'])
    ticket = AdditionalTicket(number=ticket, positive=False, who_add=operator)
    ticket.save()
    return HttpResponse('OK')

def get_ticket_price(request, ticket):
    price = TicketPrice.get_price(ticket)
    serialized_obj = serializers.serialize('json', [price])
    return JsonResponse(serialized_obj, safe=False)

def set_ticket_price(request, ticket_number, price):
    if request.POST == "POST":
        try:
            TicketPrice.set_price(ticket_number, price)
        except:
            return JsonResponse({'response': 'Error'})
        return JsonResponse({'response': 'OK'})



