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
    if request.method == 'POST':
        auth.change_ticket(id, dateform['datetime'].value(),dateform['comments'].value(), dateform['status'].value())
        return redirect('ticket_info', id)
    return render(request,'beeline_html/ticket_info.html', {'ticket_info':ticket_info, 'form': dateform})

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

def telegram_news(request):
    return render(request, 'beeline_html/telegram_news.html')

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
    homenko = Installer.parse_installers({'login': 'G800-37', 'operator': 'Хоменко', 'password': '1604'})
    return HttpResponse('Done')


def test_page(request):
    urls = [
        "www.yandex.ru", "www.google.com"
    ]
    resp = (grequests.get(u) for u in urls)
    responses = grequests.map(resp)
    a = responses[0].json()
    b = responses[1].json()
    fix_1 = a['api']['fixtures']
    api_2 = b['api']['leagues']

    context = {

        'fix_1': fix_1,
        'api_2': api_2,
    }

    return HttpResponse('Fine')

def get_schedule(request, ticket, year, month, day):
    auth = NewDesign(request.session['sell_code'], request.session['operator'], request.session['password'])
    return JsonResponse(auth.schedule(ticket, year, month, day), safe=False)