from tickets_handler.beeline_parser.manager import NewDesign,OldDesign, Worker
from django.shortcuts import render, redirect
from .form import AuthForm, DateTimeForm
from .models import Workers as WorkersModel, Installer
from django.http import HttpResponse, JsonResponse
from tickets_handler.beeline_parser import system
import grequests

@system.my_timer
def main_page(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
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


def global_search(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    tickets = WorkersModel.replace_num_worker(auth.global_search())
    return render(request, 'beeline_html/global_search.html', {'tickets':tickets})

def ticket_info(request, id):
    auth = NewDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
    ticket_info = auth.ticket_info(id)
    dateform = DateTimeForm(request.POST)
    gp_houses = auth.get_gp_ticket_serch(id)
    if request.method == 'POST':
        auth.change_ticket(id, dateform['datetime'].value(),dateform['comments'].value(), dateform['status'].value())
        return redirect('ticket_info', id)
    return render(request,'beeline_html/ticket_info.html', {'ticket_info':ticket_info, 'form': dateform,
                                                            'gp_houses': gp_houses})

def auth(request):
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
    return redirect('/login_beeline/')

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
    auth = NewDesign('G800-37', 'Хоменко', '1604')
    input = request.GET.get('streetPattern', '')
    return JsonResponse(auth.street_search_type(input), safe=False)

def get_homes_by_street(request):
    auth = NewDesign('G800-37', 'Хоменко', '1604')
    house_id = request.GET.get('house_id', '')
    data = auth.get_houses_by_street(auth.get_homes(house_id))
    return JsonResponse(data, safe=False)

def fast_house_search(request):
    return render(request, 'beeline_html/fast_house_search.html')

def get_schedule_color(request):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    house_id = request.GET.get('house_id', '')
    ticket_id = request.GET.get('ticket_id', '')
    return JsonResponse(auth.month_schedule_color(house_id, ticket_id), safe=False)

def house_info(request, house_id):
    auth = NewDesign('G800-37', 'Хоменко', '1604')
    gp_houses, areas = auth.get_gp_by_house_id(house_id)
    gp = areas + gp_houses
    return render(request, 'beeline_html/house_info.html', {'gp_houses' : gp})

def get_schedule_by_ticket_id(request, ticket, year, month, day):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    return JsonResponse(auth.schedule_interval_by_day(ticket, year, month, day, house_id=False), safe=False)

def get_schedule_by_house_id(request, house_id, year, month, day):
    auth = NewDesign('G800-37', 'Хоменко', '1604')
    return JsonResponse(auth.schedule_interval_by_day(ticket_id=False, year=year, month=month, day=day, house_id=house_id), safe=False)

