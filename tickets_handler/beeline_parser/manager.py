import json
import re
import time
import urllib.parse
from datetime import date as date
from datetime import datetime as dt
from tickets_handler.beeline_parser import system
import lxml.html
import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup
from tickets_handler.beeline_parser.date_func import current_date, last_day_current_month, url_formate_date, \
    formate_date_schedule, \
    delta_current_month, range_current_month, current_year_date, dmYHM_to_date, today, dmY_to_date, convert_utc_string
from tickets_handler.beeline_parser.text_func import find_asssigned_date, find_dns, phone9, encode
import grequests
import random
import time
import os

class Auth:
    def __init__(self, login, workercode, password):
        self.session = requests.Session()
        self.data = {}
        self.data['login'] = login
        self.data['workercode'] = workercode
        self.data['password'] = password
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
                                      ' likeGecko) Chrome/70.0.3538.110 Safari/537.36',
                        'content-type': 'application/x-www-form-urlencoded', 'upgrade-insecure-requests': '1'}
        self.auth = self.session.post('https://partnerweb.beeline.ru', self.data, headers=self.headers)
        self.auth_response = self.auth.text
        self.auth_response_status = self.check_auth()
        self.header = self.get_headers()
        self.cookies = self.get_cookie()

    def check_auth(self):
        return False if self.auth_response.count('Ошибка авторизации') else True

    def get_cookie(self):
        return self.auth.cookies.get_dict()
    def get_headers(self):
        return self.auth.headers
class Ticket:

    def __init__(self, address='', address_id='', allow_change_status='', allow_schedule='', call_time=None,
                 comments='',
                 date='', id='', name='', number='', operator='', phones='', services='', shop='', shop_id='',
                 status='',
                 ticket_paired='', type='', type_id='', phone1='', phone2='', phone3='', comment1='', comment2='',
                 comment3='', assigned_date=None, dns='', statuses='', ticket_paired_info={}):
        self.address = address  # Архангельск, проспект Новгородский, д. 186, кв. 47
        self.address_id = address_id  # 14383557
        self.allow_change_status = allow_change_status  # true
        self.allow_schedule = allow_schedule  # false
        self.call_time = call_time  # 03.01.2019 12:00
        self.comments = comments  # list[{date,id,text}]
        self.date = date  # 02.01.2019
        self.id = id  # 97251015
        self.name = name  # тест тестов тестович
        self.number = number  # 196585827
        self.operator = operator  # Леонтьев_М.А
        self.phones = phones  # list[{comment,phone}]
        self.phone1 = phone1
        self.phone2 = phone2
        self.phone3 = phone3
        self.comment1 = comment1
        self.comment2 = comment2
        self.comment3 = comment3
        self.services = services  # list[{id,name,type}] only for satelit ticket
        self.shop = shop  # Корытов Роман Валерьевич
        self.shop_id = shop_id  # 26492, 20732
        self.status = status  # Назначена в график 03.01.2019 12:00
        self.ticket_paired = ticket_paired  # 97251015
        self.type = type  # Заказ подключения/Дозаказ оборудования
        self.type_id = type_id  # 286
        self.assigned_date = assigned_date
        self.dns = dns
        self.statuses = statuses  # [0: {name: "Ждем звонка клиента", id: 16}]
        self.ticket_paired_info = ticket_paired_info

    def __repr__(self):
        return str(self.__dict__)

class Service:

    def __init__(self, IS_INAC_PRESET_id='',
                 IS_INAC_PRESET_name='',
                 IS_PRESET_id='',
                 IS_PRESET_name='',
                 VPDN_id='',
                 VPDN_name='',
                 IPTV_id='',
                 IPTV_name='',
                 TVE_id='',
                 TVE_name='',
                 W_NONSTOP_id='',
                 W_NONSTOP_name=''):
        self.W_NONSTOP_name = str(W_NONSTOP_name)
        self.W_NONSTOP_id = str(W_NONSTOP_id)
        self.TVE_name = str(TVE_name)
        self.TVE_id = str(TVE_id)
        self.IPTV_name = str(IPTV_name)
        self.IPTV_id = str(IPTV_id)
        self.VPDN_name = str(VPDN_name)
        self.VPDN_id = str(VPDN_id)
        self.IS_PRESET_name = str(IS_PRESET_name)
        self.IS_PRESET_id = str(IS_PRESET_id)
        self.IS_INAC_PRESET_name = str(IS_INAC_PRESET_name)
        self.IS_INAC_PRESET_id = str(IS_INAC_PRESET_id)

    def __repr__(self):
        return str(self.__dict__)


class OldDesign(Auth):
    """This class not use anymore, only as parent class and support old fitches.
     Partnerweb developer fix NewDesign, parse old version partnerweb is not need anymore"""

    def ticket_info(self, id):
        g = self.session.get(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}').json()
        ticket = Ticket(address=g['address'], address_id=g['address_id'],
                        allow_change_status=g['allow_change_status'],
                        allow_schedule=g['allow_schedule'], call_time=g['call_time'], comments=g['comments'],
                        date=g['date'], id=g['id'], name=g['name'], number=g['number'], operator=g['operator'],
                        phones=g['phones'],
                        services=g['services'], shop=g['shop'], shop_id=g['shop_id'], status=g['status'],
                        ticket_paired=g['ticket_paired'], type=g['type'], type_id=g['type_id'])
        return ticket

    def get_comments(self, id):
        """ In NewDesign getting automatically with tickets"""
        self.session.headers['referer'] = 'https://partnerweb.beeline.ru/ngapp'
        comments = self.session.post('https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/' + str(id))
        tree = lxml.html.fromstring(comments.content)
        tree = tree.xpath('//*/td/text()')
        tree = tree[5:-3]
        comments = []
        for i in range(0, len(tree), 2):
            print(str(str(tree[i]) + ' ' + str(tree[i + 1])).encode('ISO-8859-1').decode('unicode-escape').encode(
                'latin1').decode('utf-8', errors='ignore'))
            comments.append(i)
        return comments

    def count_created_today(self, table):
        created_today = 0
        for i in table:
            if i[2].text == 'Заявка на подключение':
                if dt.strptime(i[4].text, '%d.%m.%Y').date() == dt.now().date():
                    created_today = created_today + 1
        return created_today

    def assigned_tickets(self, table):
        assigned_tickets = []
        assigned_today = 0
        for i in table:
            if i[2].text == 'Заявка на подключение' and i[9].text == 'Назначено в график':
                full_info = self.ticket_info(i[0][0].get('id'))  # id ticket
                for comment in full_info.comments:
                    if find_asssigned_date(comment['text']):
                        assigned_date = comment['date']
                        assigned_today = assigned_today + 1 if (
                                dt.strptime(assigned_date, '%d.%m.%Y %H:%M').date() ==
                                dt.now().date()) else assigned_today
                        break
                phone1 = phone9(i[8].text)[0] if 0 < len(phone9(i[8].text)) else ''
                phone2 = phone9(i[8].text)[1] if 1 < len(phone9(i[8].text)) else ''
                phone3 = phone9(i[8].text)[2] if 2 < len(phone9(i[8].text)) else ''
                ticket = Ticket(number=i[3].text, name=i[6].text, address=i[7].text,
                                phone1=phone9(i[8].text)[0],
                                phone2=phone2,
                                phone3=phone3,
                                status=i[9].text,
                                call_time=i[10].text, operator=i[11].text,
                                id=phone1, assigned_date='', dns=find_dns(i[7].text))
                assigned_tickets.append(ticket)
        return assigned_tickets, assigned_today

    def call_for_today(self, table):
        call_today_tickets = []
        for i in table:
            if (i[2].text == 'Заявка на подключение') and (
                    i[9].text == 'Ждем звонка клиента' or i[9].text == 'Позвонить клиенту' or i[
                9].text == 'Позвонить клиенту(срочные)' or i[9].text == 'Принято в обзвон' or i[9].text == 'Резерв' or
                    i[9].text == 'Новая'):
                try:
                    timer = dt.strptime(i[10].text, '%d.%m.%Y %H.%M').date()
                except:
                    continue
                if timer <= dt.now().date() or None:
                    timer = dt.strptime(i[10].text, '%d.%m.%Y %H.%M')
                    phone1 = phone9(i[8].text)[0] if 0 < len(phone9(i[8].text)) else ''
                    phone2 = phone9(i[8].text)[1] if 1 < len(phone9(i[8].text)) else ''
                    phone3 = phone9(i[8].text)[2] if 2 < len(phone9(i[8].text)) else ''
                    ticket = Ticket(number=i[3].text, name=i[6].text, address=i[7].text,
                                    phone1=phone9(i[8].text)[0],
                                    phone2=phone2,
                                    phone3=phone3,
                                    status=i[9].text, call_time=timer, operator=i[11].text,
                                    id=phone1)
                    call_today_tickets.append(ticket)
        return call_today_tickets

    def swithed_on_tickets(self, table):
        switched_tickets = []
        swithed_on_today = 0
        for i in table:
            if i[2].text == 'Заявка на подключение' and i[9].text == 'Подключен':
                timer = ''
                try:
                    timer = dt.strptime(i[10].text, '%d.%m.%Y %H.%M').date()
                except:
                    continue
                last, cur_month, cur_year = last_day_current_month()  # filter for current month
                if (timer <= date(cur_year, cur_month, last)) and (
                        timer >= date(cur_year, cur_month, 1)):
                    swithed_on_today += 1 if timer == dt.now().date() else 0
                    phone1 = phone9(i[8].text)[0] if len(phone9(i[8].text)) else ''
                    phone2 = phone9(i[8].text)[1] if 1 < len(phone9(i[8].text)) else ''
                    phone3 = phone9(i[8].text)[2] if 2 < len(phone9(i[8].text)) else ''
                    ticket = Ticket(number=i[3].text, name=i[6].text, address=i[7].text,
                                    phone1=phone9(i[8].text)[0],
                                    phone2=phone2,
                                    phone3=phone3,
                                    status=i[9].text, call_time=timer, operator=i[11].text,
                                    id=phone1, dns=find_dns(i[7].text))
                    switched_tickets.append(ticket)
        return switched_tickets, swithed_on_today

    def three_month_tickets(self):
        date_first, date_second = range_current_month()
        assigned_tickets = []
        assigned_tickets_today = 0
        call_today_tickets = []
        switched_tickets = []
        switched_on_tickets_today = 0
        created_today_tickets = 0
        for month in range(2):
            data = dict(date_start=str(url_formate_date(date_first)), date_end=str(url_formate_date(date_second)))
            filter_page = self.session.post('https://partnerweb.beeline.ru/main/', data)
            doc = lxml.html.fromstring(filter_page.content)
            table = doc.cssselect('table.tablesorter')[0][1]
            assigned_ticket, assigned_today = self.assigned_tickets(table)
            call_today_ticket = self.call_for_today(table)
            switched_ticket, switched_on_today = self.swithed_on_tickets(table)
            assigned_tickets.extend(assigned_ticket)
            call_today_tickets.extend(call_today_ticket)
            switched_tickets.extend(switched_ticket)
            created_today_tickets = created_today_tickets + self.count_created_today(table)
            assigned_tickets_today = assigned_tickets_today + assigned_today
            switched_on_tickets_today = switched_on_tickets_today + switched_on_today
            date_first, date_second = delta_current_month(date_first, date_second)
        return assigned_tickets, assigned_tickets_today, call_today_tickets, switched_tickets, switched_on_tickets_today, created_today_tickets

    def months_report(self, num_months):
        book = Workbook()
        sheet = book.active
        row = '2'  # number row of excel
        date_first, date_second = range_current_month()
        for x in range(num_months):
            data = dict(date_start=str(url_formate_date(date_first)), date_end=str(url_formate_date(date_second)))
            filter_page = self.session.post('https://partnerweb.beeline.ru/main/', data)
            doc = lxml.html.fromstring(filter_page.content)
            table = doc.cssselect('table.tablesorter')[0][1]
            for i in table:
                if i[2].text == 'Заявка на подключение':
                    sheet['D' + row] = i[3].text  # номер заявки
                    sheet['A' + row] = i[6].text  # фио
                    sheet['B' + row] = i[7].text  # адрес
                    sheet['C' + row] = phone9(str(i[8].text))  # номер телефона
                    sheet['E' + row] = i[9].text  # статус
                    sheet['F' + row] = i[10].text  # таймер
                    sheet['G' + row] = i[11].text  # сотрудник
                    # sheet['H' + str(g)] = get_comments(str(i[3].text))
                    row = str(int(row) + 1)
            date_first, date_second = delta_current_month(date_first, date_second)
        # wight sheet columns
        sheet.column_dimensions['D'].width = str(12)
        sheet.column_dimensions['A'].width = str(30)
        sheet.column_dimensions['B'].width = str(50)
        sheet.column_dimensions['C'].width = str(25)
        sheet.column_dimensions['E'].width = str(20)
        sheet.column_dimensions['F'].width = str(16)
        sheet.column_dimensions['G'].width = str(14)
        sheet['A1'] = 'ФИО'
        sheet['B1'] = 'Адрес'
        sheet['C1'] = 'Телфон'
        sheet['D1'] = 'Номер заявки'
        sheet['E1'] = 'Статус'
        sheet['F1'] = 'Таймер'
        sheet['G1'] = 'Сотрудник'
        book.save("tableb.xlsx")

    def global_search(self):
        date_first, date_second = range_current_month()
        tickets = []
        for month in range(4):
            data = dict(date_start=str(url_formate_date(date_first)), date_end=str(url_formate_date(date_second)))
            filter_page = self.session.post('https://partnerweb.beeline.ru/main/', data)
            doc = lxml.html.fromstring(filter_page.content)
            table = doc.cssselect('table.tablesorter')[0][1]
            tickets = []
            for i in table:
                timer = ''
                try:
                    timer = dt.strptime(i[10].text, '%d.%m.%Y %H.%M').date()
                except:
                    continue
                phone2 = phone9(i[8].text)[1] if 1 < len(phone9(i[8].text)) else ''
                phone3 = phone9(i[8].text)[2] if 2 < len(phone9(i[8].text)) else ''
                ticket = Ticket(type=i[1].text, date=i[4].text, number=i[3].text, name=i[6].text, address=i[7].text,
                                phone1=phone9(i[8].text)[0],
                                phone2=phone2,
                                phone3=phone3,
                                status=i[9].text, call_time=timer, operator=i[11].text,
                                id=i[0][0].get('id'), dns=find_dns(i[7].text))
                tickets.append(ticket)
        return tickets


class Address(Auth):
    def get_street_info(self, name):
        streets = self.session.get('https://partnerweb.beeline.ru/ngapi/find_by_city_and_street/'
                                   '?cityPattern=&streetPattern=' + str(encode(name))).json()
        for street in streets:
            if street['s_city'] == 69 or street['s_city'] == 241 or street['s_city'] == 86:
                return street['city'], street['street_name'], street['s_id']

    def get_houses_by_street(self, homes_json):
        homes = []
        for home in homes_json:
            if home['h_status'] == "connected":
                home_name = f"{home['h_house']}к{home['h_building']}" if home['h_building'] else home['h_house']
                home = {'name': home_name,
                        'h_segment': home['h_segment'],
                        'h_id': home['h_id'],
                        'city_id': home['city']['ct_id']
                        }
                homes.append(home)
        return homes

    def get_homes(self, street_id):
        return self.session.get('https://partnerweb.beeline.ru/ngapi/find_by_house/' + str(street_id) + '/').json()

    def check_fraud(self, house_id, flat):
        response = self.session.get(
            f'https://partnerweb.beeline.ru/restapi/tickets/checkfraud/{house_id}/{flat}').json()
        return response

    def get_house_info(self, house_id):
        return self.session.get(f'https://partnerweb.beeline.ru/ngapi/house/{house_id}/').json()

    def get_num_house_by_id(self, ticket_id):
        address_session = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/api/ticket/'
                                           + str(ticket_id) + '?rnduncache=5466&')
        dic = address_session.json()
        address = {'num_house': dic['t_address']['h']['h_dealer']['id'],
                   'district': dic['t_address']['ar_name'],
                   'city': dic['t_address']['h']['city']}
        return address


class Schedule(Address):

    def schedule_interval_by_day(self, ticket_id, year, month, day, house_id=False):
        ar_id = ''
        if ticket_id:
            ar_id = self.get_num_house_by_id(ticket_id)['num_house']
        if house_id:
            ar_id = self.get_house_info(house_id)['h_dealer']['ar_id']
        schedule_session = self.session.get(f'https://partnerweb.beeline.ru/restapi/schedule/get_day_schedule/{ar_id}?'
                                            + urllib.parse.urlencode({'day': str(day), 'month': str(month),
                                                                      'year': str(year)})).json()
        get_free_time = schedule_session['data']['classic_schedule']
        time_intervals = []
        for key, cell in enumerate(get_free_time):
            # if ticket have other tickets in the same interval
            if cell.get('tickets_info'):
                continue
            time_intervals.append(formate_date_schedule(cell['intbegin']))
        count_interval_by_time = {i: time_intervals.count(i) for i in time_intervals}
        return count_interval_by_time

    def month_schedule_color(self, num_house, ticket_id=None):
        if num_house:
            num_house = self.get_num_house_by_id(ticket_id)['num_house']
        data_schedule = []
        schedule = self.session.get(f'https://partnerweb.beeline.ru/restapi/schedule/get_calendar/{num_house}').json()
        for data in schedule['data']['calendar']:
            month = int(data['month']) - 1  # from JS
            year = data['year']
            weeks = [day['weekdays'] for day in data['weeks']]
            clear_day = []
            for days in weeks:
                clear_day.extend([{'day': convert_utc_string(d['date']).day,
                                   'status': self.get_colors_by_status(d['status'])} for d in days if d != None])
            data_schedule.append({'days': clear_day, "month": month, "year": year})
        return (data_schedule)

    @staticmethod
    def get_colors_by_status(number):
        number = int(number)
        colors = {1: 'grey',  # close
                  2: '',  # empty
                  6: 'red',  # full
                  4: 'yellow',  # less than half
                  5: 'green',  # more than half
                  7: '',  # not created
                  3: '',  # selectted time
                  }
        return colors[number]


class Basket(Schedule):

    def get_mobile_preset(self, city_id, house_id):
        return self.session.get(
            f'https://partnerweb.beeline.ru/restapi/service/get_presets?city_id={city_id}&house_id={house_id}&is_mobile_presets=1').json()

    def get_presets(self, city_id, house_id):
        presets = self.session.get(
            f'https://partnerweb.beeline.ru/restapi/service/get_presets?city_id={city_id}&house_id={house_id}').json()
        bundles = self.session.get(
            f'https://partnerweb.beeline.ru/restapi/service/get_bundles?city_id={city_id}&house_id={house_id}').json()
        return presets

    def parse_preset(self, data):
        presets = []
        for d in data:
            presets.append({"name": d.get('name'),
             "city_id": d.get('city_id'),
             "id": d.get('id'),
             "service_type": d.get('service_type'),
                            "VPDN": d['min_cost']['VPDN']['S_ID'],
             "min_cost_total_price": d.get('min_cost_total_price')})
        return presets

class NewDesign(Basket):

    def ticket_info(self, id):
        attr = self.session.get(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}').json()
        ticket = self.ticket_instance_info(attr)
        return ticket

    def ticket_instance_info(self, attr):
        phone1, phone2, phone3 = self.get_phone123(attr)
        services = self.parse_services(attr['services']).__dict__ if attr['services'] else ''
        return Ticket(address=attr['address'], address_id=attr['address_id'],
                      allow_change_status=attr['allow_change_status'],
                      allow_schedule=attr['allow_schedule'], call_time=attr['call_time'], comments=attr['comments'],
                      date=attr['date'], id=attr['id'], name=attr['name'], number=attr['number'],
                      operator=attr['operator'], phones=attr['phones'],
                      services=services, shop=attr['shop'], shop_id=attr['shop_id'], status=attr['status'],
                      ticket_paired=attr['ticket_paired'], type=attr['type'], type_id=attr['type_id'], phone1=phone1,
                      phone2=phone2, phone3=phone3)

    def parse_services(self, data):
        services = Service()
        if data:
            for d in data:
                if d['type'] == 'IS_INAC_PRESET':
                    services.IS_INAC_PRESET_id = d['id']
                    services.IS_INAC_PRESET_name = d['name']
                if d['type'] == 'IS_PRESET':
                    services.IS_PRESET_id = d['id']
                    services.IS_PRESET_name = d['name']
                if d['type'] == 'VPDN':
                    services.VPDN_id = d['id']
                    services.VPDN_name = d['name']
                if d['type'] == 'IPTV':
                    services.IPTV_id = d['id']
                    services.IPTV_name = d['name']
                if d['type'] == 'TVE':
                    services.TVE_id = d['id']
                    services.TVE_name = d['name']
                if d['type'] == 'W_NONSTOP':
                    services.W_NONSTOP_id = d['id']
                    services.W_NONSTOP_name = d['name']
            return services
        else:
            return ''

    def get_phone123(self, attr):
        phone1 = attr['phones'][0]['phone'] if len(attr['phones']) else ''
        phone2 = attr['phones'][1]['phone'] if 1 < len(attr['phones']) else ''
        phone3 = attr['phones'][2]['phone'] if 2 < len(attr['phones']) else ''
        return phone1, phone2, phone3

    def assync_get_ticket(self, urls):
        ticket_dict = {}
        rc = [grequests.get(url, session=self.session) for url in urls]
        for index, response in enumerate(grequests.map(rc)):
            ticket_dict[index] = response.json()
        return ticket_dict

    def search_by(self, phone, city='', dateFrom=False, dateTo=False, number='', shop='', status='', pages=None):
        tickets = self.tickets(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number, phone=phone,
                               shop=shop, status=status, pages=pages)
        return tickets

    def create_ticket(self, house_id, flat, client_name, client_patrony, client_surname, phone_number_1, id,service_type,vpdn,
                      need_schedule=False):
        st = service_type.lower().replace('is_', '') + ('_service')
        data = {"house_id":house_id,"flat":flat,"create_contract":1,"client_name":client_name,
                "client_patrony":client_patrony,
                "client_surname":client_surname,"phone_number_1":phone_number_1,st:id,
                "service_type": st,
                "basket":{"MAIN":{service_type:{"S_ID":id},"VPDN":{"S_ID":vpdn}}},
                "need_schedule":False}
        if service_type == 'IS_INAC_PRESET':
            data['is_bundle'] = 0
        self.session.get(f'https://partnerweb.beeline.ru/ngapp#!/newaddress/connect_ticket/house_id/{house_id}')
        self.session.headers["origin"] = "https://partnerweb.beeline.ru"
        self.session.headers["accept-language"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        self.session.headers["x-requested-with"] = "XMLHttpRequest"
        self.session.headers['content-type'] = 'application/json'
        response = self.session.post('https://partnerweb.beeline.ru/restapi/tickets/', json.dumps(data)).json()
        return response

    def parse_creation_response(self):
        pass


    @system.my_timer
    def assigned_tickets(self, tickets):
        asig_ts, asig_ts_today, urls = [], 0, []
        for ticket in tickets:
            if (ticket.type_id == 286 or ticket.type_id == 250) \
                    and ticket.allow_schedule == False and ticket.allow_change_status == True:
                urls.append(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{ticket.id}')
        parse_tickets = self.assync_get_ticket(urls)
        a_t = [self.ticket_instance_info(value) for key, value in parse_tickets.items()]
        for ticket in a_t:
            ticket.ticket_paired_info = list([i for i in tickets if i.id == ticket.ticket_paired])[0]
            as_t = list([c['date'] for c in ticket.comments if find_asssigned_date(c['text'])])
            ticket.assigned_date = as_t[0]
            if dmYHM_to_date(ticket.assigned_date) == dt.now().date():
                asig_ts_today += 1
            asig_ts.append(ticket)
        return asig_ts, asig_ts_today

    @system.my_timer
    def switched_tickets(self, tickets):
        sw_ts, sw_ts_today = [], 0
        last, cur_month, cur_year = last_day_current_month()
        for t in tickets:
            if t.type_id == 286 or t.type_id == 250:
                if self.definde_satellit_ticket(t.status) and t.call_time != None and \
                        (date(cur_year, cur_month, 1) <= dmYHM_to_date(t.call_time) <= date(cur_year, cur_month, last)):
                    sw_ts_today += 1 if dmYHM_to_date(t.call_time) == today() else 0
                    sw_ts.append(t)
        return sw_ts, sw_ts_today

    @system.my_timer
    def tickets(self, city='', dateFrom=False, dateTo=False, number='', phone='',
                shop='', status='', pages=40):
        ticket_dict, tickets = self.async_base_tickets(city, dateFrom, dateTo, number, pages, phone, shop, status)
        for key, item in ticket_dict.items():
            for attr in item:
                attr['comments'] = attr.get('comments')
                attr['services'] = attr.get('services')
                attr['shop'] = attr.get('shop')
                attr['shop_id'] = attr.get('shop_id')
                phone1, phone2, phone3 = self.get_phone123(attr)
                ticket_paired_info = ''
                ticket = Ticket(address=attr['address'], address_id=attr['address_id'],
                                allow_change_status=attr['allow_change_status'], allow_schedule=attr['allow_schedule'],
                                call_time=attr['call_time'], comments=attr['comments'], date=attr['date'],
                                id=attr['id'],
                                name=attr['name'], number=attr['number'], operator=attr['operator'],
                                phones=attr['phones'],
                                phone1=phone1, phone2=phone2, phone3=phone3, services=attr['services'],
                                shop=attr['shop'],
                                shop_id=attr['shop_id'], status=attr['status'], ticket_paired=attr['ticket_paired'],
                                type=attr['type'], type_id=attr['type_id'])
                tickets.append(ticket)
        for ticket in tickets:
            if ticket.ticket_paired:
                ticket.ticket_paired_info = self.check_paired_ticket_info(ticket.ticket_paired, tickets)
        return tickets

    @system.my_timer
    def base_ticket_info(self, city, dateFrom, dateTo, number, pages, phone, shop, status):
        if not dateFrom and not dateTo:
            dateFrom, dateTo = current_year_date()
        ticket_dict, tickets = {}, []
        for pageCount in range(1, pages + 1):
            url = urllib.parse.urlencode(dict(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number,
                                              page=pageCount, phone=phone, shop=shop, status=status))
            new_design_ticket_info = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/?' + url).json()
            if len(new_design_ticket_info) == 0:
                break
            else:
                ticket_dict[pageCount] = new_design_ticket_info
        return ticket_dict, tickets

    def check_paired_ticket_info(self, ticket_paired_id, tickets):
        try:
            return list([i for i in tickets if i.id == ticket_paired_id])[0]
        except:
            return {'id': '', 'number': ''}

    def call_today_tickets(self, tickets):
        call_ts_today = []
        for t in tickets:
            try:
                if (t.ticket_paired_info.type_id == 1) and self.define_call_ts(t.ticket_paired_info.status)\
                        and ((dmYHM_to_date(t.ticket_paired_info.call_time) <= today())):
                    call_ts_today.append(t)
            except:
                continue
        return call_ts_today

    def count_created_today(self, tickets):
        count = 0
        for ticket in tickets:
            try:
                count += 1 if (ticket.type_id == 1) and (dmY_to_date(ticket.date) == today()) else 0
            except:
                continue
        return count

    def three_month_tickets(self):
        tickets = self.tickets()
        assigned_tickets, assigned_tickets_today = self.assigned_tickets(tickets)
        call_today_tickets = self.call_today_tickets(tickets)
        switched_tickets, switched_on_tickets_today = self.switched_tickets(tickets)
        created_today_tickets = self.count_created_today(tickets)
        return assigned_tickets, assigned_tickets_today, call_today_tickets, switched_tickets, \
               switched_on_tickets_today, created_today_tickets

    def global_search(self):
        return self.tickets()

    def definde_satellit_ticket(self, name):
        ticket_patterns = ('Подключен', 'Ошибка при конвергенции', 'Закрыта')
        name = list([w for w in name.split() if not w.isdigit()])[0]
        return True if re.search(name, ''.join(ticket_patterns)) else False

    def define_call_ts(self, name):
        ticket_patterns = ('Позвонить клиенту', 'Ждем звонка клиента',
                           'Позвонить клиенту(срочные)', 'Новая', 'Резерв', 'Принято в обзвон')
        name = list([w for w in name.split() if not w.isdigit()])[0]
        return True if re.search(name, r'|'.join(ticket_patterns)) else False

    @system.my_timer
    def async_base_tickets(self, city, dateFrom, dateTo, number, pages, phone, shop, status):
        if not dateFrom and not dateTo:
            dateFrom, dateTo = current_year_date()
        tickets, urls = [], []
        for pages in range(1, pages + 1):
            url = 'https://partnerweb.beeline.ru/restapi/tickets/?' + \
                  urllib.parse.urlencode(dict(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number,
                                              page=pages, phone=phone, shop=shop, status=status))
            urls.append(url)
        ticket_dict = self.assync_get_ticket(urls)
        return ticket_dict, tickets

    def get_gp_addres_search(self, ticket_id):
        address_session = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/api/ticket/'
                                           + str(ticket_id) + '?rnduncache=5466&')
        dic = address_session.json()
        num_house = dic['t_address']['h']['h_dealer']['id']
        areas, houses = self.get_gp_by_house_id(num_house)
        return areas, houses

    def get_gp_by_house_id(self, num_house):
        gp_session = self.session.get(f'https://partnerweb.beeline.ru/restapi/hd/global_problems_on_house/'
                                      f'{num_house}?rnd=1572982280349').json()
        areas = list([i['description'] for i in gp_session['data']['areas']])
        houses = list([i['description'] for i in gp_session['data']['houses']])
        return areas, houses

    def get_gp_ticket_search(self, id):
        gp_session = self.session.get(f'https://partnerweb.beeline.ru/restapi/schedule/validate/ticket/{id}').json()
        descriptions = gp_session['global_problems_context']['connection_related_gp_list']
        return list([i['description'] for i in descriptions])

    def street_search_type(self, name):
        streets = self.session.get('https://partnerweb.beeline.ru/ngapi/find_by_city_and_street/'
                                   '?cityPattern=&streetPattern=' + str(encode(name))).json()
        addresses = []
        for street in streets:
            if street['s_city'] == 69 or street['s_city'] == 241 or street['s_city'] == 86:
                addresses.append({'city': street['city'], 'street_name': street['street_name'], 's_id': street['s_id']})
        return addresses

    def get_full_house_info(self, id):
        return self.session.get(f'https://partnerweb.beeline.ru/ngapi/house/{id}/').json()

    def change_ticket(self, id, timer, comment='', status_id=21):
        url_status = f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}'
        comment = '; '.join(comment) if isinstance(comment, list) else comment
        if status_id == '2028':
            data_timer = {"status_id": 21, "call_time": '31.12.2028 00:00', "comment": comment}
            return self.session.post(url_status, data_timer).json()
        else:
            data_timer = {"status_id": int(status_id), "call_time": timer, "comment": comment}
            return self.session.post(url_status, data_timer).json()

    def get_personal_info(self, phone, city):
        id = self.get_q_id(phone, city)
        personal_info = self.session.get(f'https://partnerweb.beeline.ru/restapi/convergent/result_check_conv_phone/'
                                         f'{id}?rnd={random.random()}').json()
        while personal_info['data'].get('wait'):
            personal_info = self.session.get(
                f'https://partnerweb.beeline.ru/restapi/convergent/result_check_conv_phone/'
                f'{id}?rnd={random.random()}').json()
            time.sleep(3)
        return personal_info

    def get_q_id(self, phone, city):
        data = self.session.get(
            f'https://partnerweb.beeline.ru/restapi/convergent/start_check_conv_phone/{phone}?city_id={city}'
            f'&rnd={random.random()}').json()
        return data['data']['q_id']



class Worker:
    def __init__(self, name, number, master, status, url):
        self.name = name
        self.number = number
        self.master = master
        self.status = status
        self.url = url

    @staticmethod
    def get_workers(auth):
        workers = []
        workers_html = auth.session.get('https://partnerweb.beeline.ru/partner/workers/').text
        soup = BeautifulSoup(workers_html, 'lxml')
        table_body = soup.find('table', attrs={'class': 'form-table'})
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [x.text.strip() for x in cols]
            a = 'https://partnerweb.beeline.ru' + row.find('a').get('href') if row.find('a') is not None else []
            if len(cols) != 0:
                cols[3] = True if cols[3] == 'Включен' else False
                worker = Worker(cols[0], cols[1], cols[2], cols[3], a)
                workers.append(worker)
        return workers


if __name__ == '__main__':
    auth = NewDesign(os.getenv('SELL_CODE'),os.getenv('S_OPERATOR'),os.getenv('S_PASSWORD'))
    print(auth.headers)
    print(auth.cookies)

