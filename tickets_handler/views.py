from tickets_handler.beeline_parser.manager import NewDesign, Worker, Auth
from django.shortcuts import render, redirect
from .form import AuthForm, DateTimeForm, CreateTicketForm, Feedback
from .models import Workers as WorkersModel, Installer, AdditionalTicket, Employer
from django.http import HttpResponse
from tickets_handler.beeline_parser import system
from django.contrib import messages
from tickets_handler.beeline_parser.mail import assign_mail_ticket, fraud_mail_ticket, feedback_mail

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
        operator = WorkersModel.objects.filter(number=worker.number)
        if not operator:
            WorkersModel(name=worker.name, number=worker.number, master=worker.master, status=worker.status,
                             url=worker.url).save()
            continue
        operator.update(name=worker.name, master=worker.master, status=worker.status, url=worker.url)
    return HttpResponse('Done')

def update_installers(request):
    Installer.parse_installers({'login': request.session['sell_code'], 'operator': request.session['operator'],
                                'password': request.session['password']})
    return HttpResponse('Done')

def get_installers(request):
    installers = Installer.objects.all()
    return render(request, 'beeline_html/installers.html', {'installers' : installers})


def fast_house_search(request):
    return render(request, 'beeline_html/fast_house_search.html')


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
        res_data = auth.check_fraud(house_id, p_form['flat'].value())
        if res_data['data']:
            create_ticket_form = auth.create_ticket(house_id, p_form['flat'].value(), p_form['client_name'].value(),
                                                    p_form['client_patrony'].value(), p_form['client_surname'].value(),
                                                    p_form['phone_number_1'].value(), bundel_id, service_type, vpdn)
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
            fraud_mail_ticket(ticket)
            return HttpResponse(
                'Ваша заявка содержит активный договор на адресе '
                'и была отправлена супервайзеру для дальнейшего рассмотрения'
            )
    return render(request, 'beeline_html/house_info.html', {'gp_houses' : gp, 'name': house_full_name,
                                                            'p_form' : p_form})


def logout(request):
    request.session['sell_code'], request.session['operator'], request.session['password'] = '', '',''
    return redirect('login')


def check_number(request):
    return render(request, 'beeline_html/check_number.html')


def delete_additional_ticket(request, ticket):
    operator = WorkersModel.objects.get(number=request.session['operator'])
    ticket = AdditionalTicket(number=ticket, positive=False, who_add=operator)
    ticket.save()
    return HttpResponse('OK')

def add_additional_ticket(request):
    if request.is_ajax():
        if request.method == "POST":
            AdditionalTicket.add(request.body)
    return HttpResponse('Done')

def show_additional_tickets(request, operator):
    return


def send_mail(request):
    if request.is_ajax():
        if request.method == "POST":
            assign_mail_ticket(request.body)
    return HttpResponse('Отправленно')

def index(request):
    return render(request, 'beeline_html/index.html')

def feedback(request):
    form = Feedback()
    if request.method == "POST":
        form = Feedback(request.POST)
        text = { 'descr' : form['descr'].value(), 'agent' : request.session['operator']}
        feedback_mail(text)
    return render(request, 'beeline_html/feedback.html', {'form':form})


def ism_schedule(request):
    return render(request, 'beeline_html/ism_schedule.html')