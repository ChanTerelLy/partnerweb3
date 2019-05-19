from .models import AllAssigned, CallToday
from beeline.beeline import Auth,NewDesign,OldDesign
from django.shortcuts import render, get_object_or_404, redirect
from .form import AuthForm
from .models import Auth
from django.http import HttpResponse

def main_page(request, master1, master2, master3):
    accounts = OldDesign(master1,master2,master3)
    all_assigned_tickets, all_assigned_today, all_call_for_today, all_switched_on_tickets,\
    all_switched_on_today, all_created_today_tickets = [],0,[],[],0,0
    assigned_tickets, assigned_today, call_for_today, switched_on_tickets, \
    switched_on_today, created_today_tickets = accounts.three_month_tickets()
    all_assigned_tickets.extend(assigned_tickets)
    all_assigned_today += assigned_today
    all_call_for_today.extend(call_for_today)
    all_switched_on_tickets.extend(switched_on_tickets)
    all_switched_on_today += switched_on_today
    all_created_today_tickets += created_today_tickets
    return render( request,'tickets_main_page.html',
              {'assigned_tickets':all_assigned_tickets,
               'call_for_today':all_call_for_today,
               'switched_on_tickets': all_switched_on_tickets,'assigned_today':all_assigned_today,'switched_on_today':
                   all_switched_on_today, 'created_today_tickets': all_created_today_tickets})

def global_search(request, master1,maser2,master3):
    accounts = OldDesign( master1,maser2,master3)
    global_search_tickets = accounts.three_month_tickets()
    return render(request, 'global_search.html', {'tickets':global_search_tickets})

def ticket_info(request, id,  master1,maser2,master3):
    accounts = OldDesign( master1,maser2,master3)
    ticket_info = accounts.ticket_info(id)

    return render(request,'ticket_info.html', {'ticket_info':ticket_info})

def auth(request):
    form = AuthForm(request.POST)
    if request.method == 'POST':
        form = AuthForm(request.POST)
        master = [form['sell_code'].value(), form['operator'].value(), form['password'].value()]
        if form.is_valid():
            #return redirect('main_page_tickets')
            return main_page(request, master[0], master[1], master[2])
    return render(request, 'auth_beeline.html', {'form': form})