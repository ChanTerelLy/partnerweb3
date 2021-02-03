import os

from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote

from partnerweb_parser.manager import NewDesign, Auth
from tickets_handler.models import Employer, TicketSource, AUP
import jsonpickle
from types import SimpleNamespace
import json

from tickets_handler.tasks import update_date_for_assigned


def check_fraud(request, city_id, house_id, flat):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    if auth.account_type != 4:
        employer = Employer.objects.get(profile_name=request.session['operator'])
        auth = NewDesign(os.getenv('SELL_CODE'),
                         employer.operator.number,
                         employer.operator_password)
    res_data = auth.check_fraud(house_id, flat)
    if res_data['data']:
        return JsonResponse({'result': 'Можно создавать заявку'})
    else:
        return JsonResponse({'result': res_data['metadata']['message']})

#TODO:remove or add price functionality
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


def get_mobile_presets_json(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    city_id, house_id = request.GET.get('city_id'), request.GET.get('house_id')
    data = auth.get_mobile_presets(city_id, house_id)
    return JsonResponse(data, safe=False)


def get_presets_json(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    city_id, house_id = request.GET.get('city_id'), request.GET.get('house_id')
    data = auth.get_presets(city_id, house_id)
    return JsonResponse(data, safe=False)


def get_schedule_by_ticket_id(request, ticket, year, month, day):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    return JsonResponse(auth.schedule_interval_by_day(ticket, year, month, day, house_id=False), safe=False)


def get_schedule_by_house_id(request, city_id, house_id, year, month, day):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    return JsonResponse(
        auth.schedule_interval_by_day(ticket_id=False, year=year, month=month, day=day, house_id=house_id), safe=False)


def get_personal_info(request):
    phone = request.GET.get('phone')
    city = request.GET.get('city')
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    return JsonResponse(auth.get_personal_info(phone, city), safe=False)


def ticket_info_json(request, id):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    ticket = auth.ticket_info(id).__dict__
    return JsonResponse(ticket, safe=False)


def street_search(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    input = request.GET.get('streetPattern', '')
    return JsonResponse(auth.street_search_type(input), safe=False)


def get_homes_by_street(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    street_id = request.GET.get('street_id', '')
    data = auth.get_houses_by_street(auth.get_homes(street_id))
    return JsonResponse(data, safe=False)


def get_schedule_color(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    house_id = request.GET.get('house_id', '')
    ticket_id = request.GET.get('ticket_id', '')
    return JsonResponse(auth.month_schedule_color(house_id, ticket_id), safe=False)

@csrf_exempt
def get_assigned_tickets(request):
    if request.method == "POST":
        params = unquote(request.POST.urlencode()).split('&')
        data = {param.split('=')[0]: param.split('=')[1] for param in params if param}
        auth = NewDesign(os.getenv('SELL_CODE'), data['operator'], data['password'])
        tickets = auth.retrive_tickets()
        assigned_tickets, assigned_tickets_today = auth.assigned_tickets(tickets)
        as_t = jsonpickle.encode(assigned_tickets)
        return JsonResponse({'assigned_tickets': as_t,
                         'assigned_tickets_today': assigned_tickets_today}, safe=False)

@csrf_exempt
def get_call_today_tickets(request):
    if request.method == "POST":
        params = unquote(request.POST.urlencode()).split('&')
        data = {param.split('=')[0]: param.split('=')[1] for param in params if param}
        auth = NewDesign(os.getenv('SELL_CODE'), data['operator'], data['password'])
        tickets = auth.retrive_tickets()
        call_today_tickets = auth.call_today_tickets(tickets)
        t = jsonpickle.encode(call_today_tickets)
        return JsonResponse({'tickets' : t}, safe=False)

@csrf_exempt
def get_switched_tickets(request):
    if request.method == "POST":
        params = unquote(request.POST.urlencode()).split('&')
        data = {param.split('=')[0]: param.split('=')[1] for param in params if param}
        auth = NewDesign(os.getenv('SELL_CODE'), data['operator'], data['password'])
        tickets = auth.retrive_tickets()
        switched, count = auth.switched_tickets(tickets)
        t = jsonpickle.encode(switched)
        return JsonResponse({'tickets' : t, 'count' : count}, safe=False)



def get_count_created_today(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    tickets = auth.retrive_tickets()
    created_today_tickets = auth.count_created_today(tickets)
    return JsonResponse(created_today_tickets, safe=False)


def source_tickets(request):
    if request.GET.get('add', ''):
        text = json.loads(request.body.decode('utf-8'))
        d = SimpleNamespace(**text)  # convert dict to variable
        TicketSource.add_source(d.ticket_id, d.source, d.operator)
        return JsonResponse({'status': 'done'})
    if request.GET.get('show', ''):
        try:
            response = {'source': TicketSource.find_source(request.GET.get('show'))}
            return JsonResponse(response)
        except:
            return JsonResponse({'source': "Не определено"})


def get_ctn_info(request):
    ctn = request.GET.get('ctn', '')
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    data = auth.get_ctn_info(ctn)
    return JsonResponse(data)


def change_phone_number(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    ticket_id = request.GET.get('ticket_id', '')
    if request.is_ajax():
        if request.method == "POST":
            response = auth.change_phone_info(ticket_id, request.body)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


def get_aup_email(request):
    aup = AUP.objects.all()
    return JsonResponse(serializers.serialize('json', aup), safe=False)


def assign_ticket(request):
    auth = NewDesign(os.getenv('SELL_CODE'), request.session['operator'], request.session['password'])
    if request.method == "POST":
        payload = json.loads(request.body)
        data = {"tickets": [payload['ticket_id']],
                "cell": payload['cell'],
                "intbegin": payload['intbegin'],
                "intend": payload['intend'],
                "entrance": payload['entrance'],
                "floor": payload['floor'],
                "code": "0",
                "confirmation": ""}
        response = auth.assign_ticket(data)
        return JsonResponse({'status': response})

def error500(request):
    return HttpResponse(status=500)


@csrf_exempt
def api_login(request):
    if request.method == "POST":
        params = request.POST.urlencode().split('&')
        data = {param.split('=')[0]: param.split('=')[1] for param in params if param}
        request.session['operator'], request.session['password'] = data['operator'], data['password']
        auth = Auth(os.getenv('SELL_CODE'), data['operator'], data['password'])
        status = auth.check_auth_status()
        if (status):
            account_type = auth.account_type
            request.session['operator'], request.session['password'] = data['operator'], data['password']
            request.session.save()
            key = request.session.session_key
            return JsonResponse({'success': True, 'account_type' : account_type, 'sessionid': key})
        else:
            return JsonResponse({'success': False, 'error': 'Ошибка Аутентификации, неправильный логин или пароль!'})
