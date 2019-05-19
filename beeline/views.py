from .models import AllAssigned, CallToday
from beeline.beeline import Auth,NewDesign,OldDesign
from django.shortcuts import render, get_object_or_404, redirect
from .form import AuthForm


def main_page(request):
    accounts = OldDesign(request.session['sell_code'], request.session['operator'],request.session['password'])
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
    request.session.set_expiry(600)
    return render( request,'tickets_main_page.html',
              {'assigned_tickets':all_assigned_tickets,
               'call_for_today':all_call_for_today,
               'switched_on_tickets': all_switched_on_tickets,'assigned_today':all_assigned_today,'switched_on_today':
                   all_switched_on_today, 'created_today_tickets': all_created_today_tickets})

def global_search(request):
    accounts = OldDesign( request.session['sell_code'],request.session['operator'],request.session['password'])
    global_search_tickets = accounts.three_month_tickets()
    return render(request, 'global_search.html', {'tickets':global_search_tickets})

def ticket_info(request, id):
    accounts = OldDesign(request.session['sell_code'],request.session['operator'],request.session['password'])
    ticket_info = accounts.ticket_info(id)
    return render(request,'ticket_info.html', {'ticket_info':ticket_info})

def auth(request):
    form = AuthForm(request.POST)
    if request.method == 'POST':
        form = AuthForm(request.POST)
        request.session['sell_code'], request.session['operator'],request.session['password'] = form['sell_code'].value(), form['operator'].value(), form['password'].value()
        if form.is_valid():
            return redirect('main_page_tickets')
    return render(request, 'auth_beeline.html', {'form': form})