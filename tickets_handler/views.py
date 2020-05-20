from partnerweb_parser.manager import NewDesign, Worker, Auth
from django.shortcuts import render, redirect
from .form import AuthForm, DateTimeForm, CreateTicketForm, FindAnythingForm, FraudTicketSendForm
from .models import Workers as WorkersModel, Installer, AdditionalTicket, Employer, AssignedTickets
from django.http import HttpResponse
from partnerweb_parser import system
from django.contrib import messages
from partnerweb_parser.mail import EmailSender
from .decorators import check_access
from django.http import JsonResponse, HttpResponseServerError
from django.core.paginator import Paginator
import jsonpickle
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache import cache
from datetime import datetime
import pytz
from partnerweb_parser.manager import NewDesign
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)



@system.my_timer
@check_access
def tickets(request):
    tz = pytz.timezone('Europe/Moscow')
    moscow_now = datetime.now(tz)
    code, operator, password = request.session['sell_code'], request.session['operator'], request.session['password']
    if Auth(code, operator, password).auth_status:
        if request.method == 'GET':
            auth = NewDesign(code, operator, password)
            assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
            switched_on_today, created_today_tickets, all_tickets = auth.three_month_tickets()
            cache.set(request.session['operator'], {'assigned_tickets': assigned_tickets,
                                                    'assigned_today': assigned_today,
                                                    'call_for_today': call_for_today,
                                                    'switched_on_tickets': switched_on_tickets,
                                                    'switched_on_today': switched_on_today,
                                                    'created_today_tickets': created_today_tickets,
                                                    'all_tickets': all_tickets, 'timestamp': moscow_now})
            return render(request, 'beeline_html/main_page_tickets.html',
                          {'assigned_tickets': WorkersModel.replace_num_worker(assigned_tickets),
                           'call_for_today': WorkersModel.replace_num_worker(call_for_today),
                           'switched_on_tickets': WorkersModel.replace_num_worker(
                               AdditionalTicket.clear_switched_tickets(switched_on_tickets, all_tickets)
                           ),
                           'assigned_today': assigned_today, 'switched_on_today': switched_on_today,
                           'created_today_tickets': created_today_tickets, 'all_tickets' : all_tickets, 'timestamp': moscow_now})
    else:
        messages.error(request, f'Ошибка Аутентификации, неправильный логин или пароль!')
        request.session['sell_code'], request.session['operator'], request.session['password'] = '','',''
        return redirect('login')

@system.my_timer
@check_access
def tickets_rapid(request):
    if request.method == 'GET' and (cache.get(request.session['operator']) or cache.get('supervisors_tickets')):
        cache_tickets = cache.get(request.session['operator'])
        if cache_tickets:
            assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
            switched_on_today, created_today_tickets, all_tickets, timestamp = cache_tickets['assigned_tickets'], \
                                                                    cache_tickets['assigned_today'], cache_tickets[
                                                                        'call_for_today'], cache_tickets[
                                                                        'switched_on_tickets'], \
                                                                    cache_tickets['switched_on_today'], cache_tickets[
                                                                        'created_today_tickets'], cache_tickets[
                                                                        'all_tickets'], cache_tickets['timestamp']
            return render(request, 'beeline_html/main_page_tickets.html',
                          {'assigned_tickets': WorkersModel.replace_num_worker(assigned_tickets),
                           'call_for_today': WorkersModel.replace_num_worker(call_for_today),
                           'switched_on_tickets': WorkersModel.replace_num_worker(
                               AdditionalTicket.clear_switched_tickets(switched_on_tickets, all_tickets)
                           ),
                           'assigned_today': assigned_today, 'switched_on_today': switched_on_today,
                           'created_today_tickets': created_today_tickets, 'all_tickets': all_tickets, 'timestamp': timestamp})
        else:
            cache_tickets = cache.get('supervisors_tickets')
            assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
            switched_on_today, created_today_tickets, all_tickets,timestamp = cache_tickets['assigned_tickets'], \
                                                                    cache_tickets['assigned_today'], cache_tickets[
                                                                        'call_for_today'], cache_tickets[
                                                                        'switched_on_tickets'], \
                                                                    cache_tickets['switched_on_today'], cache_tickets[
                                                                        'created_today_tickets'], cache_tickets[
                                                                        'all_tickets'], cache_tickets['timestamp']
            assigned_tickets = list([a for a in assigned_tickets if a.operator == request.session['operator']])
            call_for_today = list([a for a in call_for_today if a.operator == request.session['operator']])
            switched_on_tickets = list([a for a in switched_on_tickets if a.operator == request.session['operator']])
            all_tickets = list([a for a in all_tickets if a.operator == request.session['operator']])
            created_today_tickets = NewDesign.count_created_today(all_tickets)
            #very weird desicion, dont think about it
            s = filter(lambda number:number != 0, list([NewDesign.count_switched(0, t) for t in switched_on_tickets]))
            switched_on_today = len(list(s))
            #legacy fixed by js code on template
            assigned_today = 0

            return render(request, 'beeline_html/main_page_tickets.html',
                          {'assigned_tickets': WorkersModel.replace_num_worker(assigned_tickets),
                           'call_for_today': WorkersModel.replace_num_worker(call_for_today),
                           'switched_on_tickets': WorkersModel.replace_num_worker(
                               AdditionalTicket.clear_switched_tickets(switched_on_tickets, all_tickets)
                           ),
                           'assigned_today': assigned_today, 'switched_on_today': switched_on_today,
                           'created_today_tickets': created_today_tickets, 'all_tickets': all_tickets, 'timestamp' : timestamp})
    else:
        return redirect('main_page_tickets')


@system.my_timer
@check_access
def tickets_redis_json(request):
    tz = pytz.timezone('Europe/Moscow')
    moscow_now = datetime.now(tz)
    auth_r = NewDesign('G800-37', 'Корытов', '123456Qq')
    auth_h = NewDesign('G800-37', 'Хоменко', '1604')
    assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
    switched_on_today, created_today_tickets, all_tickets = auth_r.three_month_tickets()
    cache.set('Корытов', {'assigned_tickets': assigned_tickets,
                                            'assigned_today': assigned_today,
                                            'call_for_today': call_for_today,
                                            'switched_on_tickets': switched_on_tickets,
                                            'switched_on_today': switched_on_today,
                                            'created_today_tickets': created_today_tickets,
                                            'all_tickets': all_tickets, 'timestamp': moscow_now})
    h_assigned_tickets, h_assigned_today, h_call_for_today, h_switched_on_tickets, \
    h_switched_on_today, h_created_today_tickets, h_all_tickets = auth_h.three_month_tickets()
    cache.set('Хоменко', {'assigned_tickets': h_assigned_tickets,
                                            'assigned_today': h_assigned_today,
                                            'call_for_today': h_call_for_today,
                                            'switched_on_tickets': h_switched_on_tickets,
                                            'switched_on_today': h_switched_on_today,
                                            'created_today_tickets': h_created_today_tickets,
                                            'all_tickets': h_all_tickets, 'timestamp': moscow_now})
    assigned_tickets += h_assigned_tickets
    assigned_today += h_assigned_today
    call_for_today += h_call_for_today
    switched_on_tickets += h_switched_on_tickets
    switched_on_today += h_switched_on_today
    created_today_tickets += h_created_today_tickets
    all_tickets += h_all_tickets
    cache.set('supervisors_tickets', {'assigned_tickets': assigned_tickets,
                                            'assigned_today': assigned_today,
                                            'call_for_today': call_for_today,
                                            'switched_on_tickets': switched_on_tickets,
                                            'switched_on_today': switched_on_today,
                                            'created_today_tickets': created_today_tickets,
                                            'all_tickets': all_tickets, 'timestamp': moscow_now})
    return JsonResponse({'status':'ok'}, safe=False)

@system.my_timer
@check_access
def global_search(request):
    tickets = ''
    if cache.get(request.session['operator']):
        tickets = Paginator(cache.get(request.session['operator'])['all_tickets'], 100)
        page_number = request.GET.get('page', 1)
        page_obj = tickets.get_page(page_number)
        return render(request, 'beeline_html/global_search.html', {'page_obj': page_obj})
    else:
        auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
        all_tickets = auth.global_search()
        cache.set(request.session['operator'], all_tickets)
        tickets = Paginator(all_tickets, 100)
        page_number = request.GET.get('page', 1)
        page_obj = tickets.get_page(page_number)
        return render(request, 'beeline_html/global_search.html', {'page_obj': page_obj})

@check_access
def ticket_info(request, id):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    show_comments = request.GET.get('show_comments', '')
    json = request.GET.get('json', '')
    insert_assigned = request.GET.get('insert_assigned', '')
    ticket_info = auth.ticket_info(id)
    if show_comments:
        return JsonResponse(ticket_info.comments[:int(show_comments)], safe=False)
    elif json:
        return JsonResponse(jsonpickle.encode(ticket_info), safe=False)
    elif insert_assigned:
        AssignedTickets.update(ticket_info, request)
        return JsonResponse(jsonpickle.encode(ticket_info), safe=False)
    ticket_info = auth.ticket_info(id)
    dateform = DateTimeForm(request.POST)
    try:
        gp_houses = auth.get_gp_ticket_search(id)
    except Exception as e:
        print(e)
        gp_houses = None
    if request.method == 'POST':
        auth.change_ticket(id, dateform['datetime'].value(),dateform['comments'].value(), dateform['status'].value())
        return redirect('ticket_info', id)
    return render(request,'beeline_html/ticket_info.html', {'ticket_info':ticket_info, 'form': dateform,
                                                            'gp_houses': gp_houses})


def login(request):
    form = AuthForm(request.POST)
    if request.method == 'POST':
        request.session['sell_code'], request.session['operator'],request.session['password'] = form['sell_code'].value(), form['operator'].value(), form['password'].value()
        if form.is_valid() and \
                NewDesign(request.session['sell_code'], request.session['operator'],request.session['password']).\
                        check_auth_status():
            return redirect('main_page_rapid')
        else:
            messages.error(request, f'Ошибка Аутентификации, неправильный логин или пароль!')
            request.session['sell_code'], request.session['operator'], request.session['password'] = '', '', ''
            return redirect('login')
    return render(request, 'beeline_html/login_beeline.html', {'form': form})

def redirect_auth(request):
    return redirect('login')


@check_access
def update_workers(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    for worker in Worker.get_workers(auth):
        operator = WorkersModel.objects.filter(number=worker.number)
        if not operator:
            WorkersModel(name=worker.name, number=worker.number, master=worker.master, status=worker.status,
                             url=worker.url).save()
            continue
        operator.update(name=worker.name, master=worker.master, status=worker.status, url=worker.url)
    return HttpResponse('Done')

@check_access
def update_installers(request):
    Installer.parse_installers({'login': request.session['sell_code'], 'operator': request.session['operator'],
                                'password': request.session['password']})
    return HttpResponse('Done')


@check_access
def house_info(request, city_id, house_id):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    if auth.account_type != 4:
        employer = Employer.objects.get(profile_name=request.session['operator'])
        auth = NewDesign(request.session['sell_code'],
                         employer.operator.number,
                         employer.operator_password)
    gp_houses, areas = auth.get_gp_by_house_id(house_id)
    house_full_name = auth.get_full_house_info(house_id)['house_address']
    p_form = CreateTicketForm()
    gp = areas + gp_houses
    if request.method == 'POST':
        p_form = CreateTicketForm(request.POST)
        bundel_id, service_type, vpdn, service_name = p_form['basket'].value().split(';')
        if p_form.is_valid():
            res_data = auth.check_fraud(house_id, p_form['flat'].value())
            if res_data['data']:
                try:
                    create_ticket_form = auth.create_ticket(house_id, p_form['flat'].value(), p_form['client_name'].value(),
                                                            p_form['client_patrony'].value(), p_form['client_surname'].value(),
                                                            p_form['phone_number_1'].value(), bundel_id, service_type, vpdn)
                except Exception as e:
                    EmailSender().error_mail(e)
                    return HttpResponseServerError("Что то пошло не так")
                return redirect('ticket_info', create_ticket_form['data']['ticket_id'])
            else:
                ticket = {'mail_to' : Employer.find_master(request.session['operator']).email,
                          'client_name':  f" {p_form['client_name'].value()}"
                                          f" {p_form['client_patrony'].value()}"
                                          f" {p_form['client_surname'].value()}",
                          'phone' : p_form['phone_number_1'].value(),
                          'tariff' : service_name,
                          'agent' : request.session['operator'],
                          'address' : f'{house_full_name} кв {p_form["flat"].value()}'
                          }
                request.session['fraud_ticket'] = ticket
                return redirect('fraud_ticket_send')
    return render(request, 'beeline_html/house_info.html', {'gp_houses' : gp, 'name': house_full_name,
                                                            'p_form' : p_form})

def fraud_ticket_send(request):
    form = FraudTicketSendForm()
    if request.method == 'POST':
        form = FraudTicketSendForm(request.POST)
        fraud_ticket = request.session['fraud_ticket']
        fraud_ticket['datetime'] = form['datetime'].value()
        fraud_ticket['comment'] = form['comment'].value()
        fraud_ticket['assigned'] = form['assigned'].value()
        EmailSender().fraud_ticket(fraud_ticket)
        messages.success(request, f'Заявка успешно отправлена супервайзеру')
        return redirect('main_page_rapid')
    return render(request, 'beeline_html/fraud_ticket_send_form.html', {'form': form})
def logout(request):
    request.session['sell_code'], request.session['operator'], request.session['password'] = '', '',''
    return redirect('login')


def send_mail(request):
    if request.is_ajax():
        if request.method == "POST":
            EmailSender().assign_mail_ticket(request.body)
    return HttpResponse('Отправленно')

def find_anything(request):
    form = FindAnythingForm(request.POST)
    if request.method == 'POST':
        data = form['data'].value()
        all_tickets = cache.get('supervisors_tickets')['all_tickets']
        filter_tickets = []

        # check phones and ticket nubmer
        if data[0].isdigit():
            # phone checks
            if data[0] == '9':
                data = int(data)
                for t in all_tickets:
                    try:
                        if [t for p in t.phones if data in p.values()]:
                            filter_tickets.append(t)
                        else:
                            continue
                    except:
                        continue
                return render(request, 'beeline_html/find_anything_result.html', {'tickets' : filter_tickets})
            else:
                for t in all_tickets:
                    data = int(data)
                    try:
                        if data in [t.number, t.ticket_paired_info.number]:
                            filter_tickets.append(t)
                        else:
                            continue
                    except Exception as e:
                        print(e)
                        continue
                return render(request, 'beeline_html/find_anything_result.html', {'tickets': filter_tickets})
        #find by name or street
        else:
            find_values = data.split()
            for t in all_tickets:
                if any(x in t.name.lower() for x in find_values):
                    filter_tickets.append(t)
                if all(x in t.address.lower() for x in find_values):
                    filter_tickets.append(t)
        return render(request, 'beeline_html/find_anything_result.html', {'tickets': filter_tickets})

    return render(request, 'beeline_html/find_anything.html', {'form': form})

