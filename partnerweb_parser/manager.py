import asyncio
import json
import os
import re
import urllib.parse
from datetime import date as date

import aiohttp

from partnerweb_parser import system
import lxml.html
import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup
from partnerweb_parser.date_func import last_day_current_month, url_formate_date, \
    formate_date_schedule, \
    delta_current_month, range_current_month, current_year_date, dmYHM_to_date, today, dmY_to_date, convert_utc_string
from partnerweb_parser.text_func import find_asssigned_date, find_dns, phone9, encode, get_phone123
import grequests
import random
import time
from datetime import datetime as dt
from datetime import timedelta
import datetime

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
        self.auth_status = self.check_auth_status()
        self.header = self.get_headers()
        self.cookies = self.get_cookie()
        self.account_type = self.get_account_type(self.user_rights())

    def check_auth_status(self):
        return False if self.auth_response.count('Ошибка авторизации') else True

    def get_cookie(self):
        return self.auth.cookies.get_dict()
    def get_headers(self):
        return self.auth.headers

    def user_rights(self):
        try:
            data = self.session.get('https://partnerweb.beeline.ru/restapi/auth/current-user/').json()
        except Exception as e:
            print(e)
            return None
        return data

    def check_auth_access(self, user_info):
            if user_info.get('detail') == 'Учетные данные не были предоставлены.':
                return
            else:
                return True

    def get_account_type(self, user_info):
        if self.check_auth_access(user_info):
            return user_info.get('data').get('type')
        else:
            return 0


class Ticket:

    def __init__(self, address='', address_id='', allow_change_status='', allow_schedule='', call_time=None,
                 comments='',
                 date='', id='', name='', number='', operator='', phones='', services='', shop='', shop_id='',
                 status='',
                 ticket_paired='', type='', type_id='', phone1='', phone2='', phone3='', comment1='', comment2='',
                 comment3='', assigned_date=None, dns='', statuses='', ticket_paired_info={}, status_id=''):
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
        self.status = self.clear_status(status)  # Назначена в график 03.01.2019 12:00
        self.ticket_paired = ticket_paired  # 97251015
        self.type = type  # Заказ подключения/Дозаказ оборудования
        self.type_id = type_id  # 286
        self.assigned_date = assigned_date
        self.dns = dns
        self.statuses = statuses  # [0: {name: "Ждем звонка клиента", id: 16}]
        self.ticket_paired_info = ticket_paired_info
        self.status_id = status_id


    def clear_status(self, s):
        n = ''.join([i for i in s if (not i.isdigit()) and (i not in [':', '.'])])
        return n

    def __repr__(self):
        return str(self.__dict__)

class TicketParser:

    def ticket_instance_info(self, attr):
        phone1, phone2, phone3 = get_phone123(attr)
        ticket = Ticket(address=attr['address'], address_id=attr['address_id'],
                        allow_change_status=attr['allow_change_status'],
                        allow_schedule=attr['allow_schedule'], call_time=attr['call_time'], comments=attr['comments'],
                        date=attr['date'], id=attr['id'], name=attr['name'], number=attr['number'],
                        operator=attr['operator'], phones=attr['phones'],
                        services=attr['services'], shop=attr['shop'], shop_id=attr['shop_id'], status=attr['status'],
                        ticket_paired=attr['ticket_paired'], type=attr['type'], type_id=attr['type_id'], phone1=phone1,
                        phone2=phone2, phone3=phone3, status_id=attr['status_id'], statuses=attr['statuses'])
        as_t = list([c['date'] for c in ticket.comments if find_asssigned_date(c['text'])])
        ticket.assigned_date = as_t[0] if as_t else None
        return ticket


#TODO:not working in django thread
class AsyncTicketParser(TicketParser):

    def __init__(self, login, workercode, password):
        self.data = {}
        self.data['login'] = login
        self.data['workercode'] = workercode
        self.data['password'] = password
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
                                      ' likeGecko) Chrome/70.0.3538.110 Safari/537.36',
                        'content-type': 'application/x-www-form-urlencoded', 'upgrade-insecure-requests': '1'}

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    async def tickets_info(self, ids):
        tasks = []
        urls = list([f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}' for id in ids])
        urls += f'https://partnerweb.beeline.ru/restapi/schedule/validate/ticket/{ids[0]}'
        async with aiohttp.ClientSession() as session:
            d = await session.get('http://www.google.com')
            await self.login(session)
            for url in urls:
                tasks.append(self.fetch(session, url))
            return asyncio.gather(*tasks)

    async def login(self, session):
        self.auth = await session.post('https://partnerweb.beeline.ru', data=self.data, headers=self.headers)

    def parse_gp(self, data):
        descriptions = data['global_problems_context']['connection_related_gp_list']
        return list([i['description'] for i in descriptions])

    def get_ticket_info_datas(self, auth, id, satelit_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tickets_info = loop.run_until_complete(auth.tickets_info([id, satelit_id]))

class OldDesign(Auth):
    """This class not use anymore, only as parent class and support old fitches.
     Partnerweb developer fix NewDesign, parse old version partnerweb is not need anymore"""

    def ticket_info(self, id):
        g = self.session.get(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}').json()
        ticket = Ticket(address=g['address'], address_id=g['address_id'],
                        allow_change_status=g['allow_change_status'],
                        allow_schedule=g['allow_schedule'], call_time=g['call_time'], comments=g['comments'],
                        date=g['date'], id=g['id'], name=g['name'], number=g['number'], operator=g['operator'],
                        phones=g['phones'],services=g['services'], shop=g['shop'], shop_id=g['shop_id'],
                        status=g['status'], ticket_paired=g['ticket_paired'], type=g['type'],
                        type_id=g['type_id'])
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
            cities = list([int(id) for id in os.getenv('CITIES_ID').split(',')])
            if street['s_city'] in cities:
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
        url = f'https://partnerweb.beeline.ru/restapi/tickets/checkfraud/{house_id}/{flat}?rnd={round(random.random(), 16)}'
        response = self.session.get(url).json()
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

    def get_id_by_fullname(self, street, house, building):
        street_id = self.street_search_type(street)[0]['s_id'] #
        houses = self.get_homes(street_id)
        for h in houses:
            print(h['h_building'])
            print(h['h_house'])
            if str(h['h_house']) == str(house) and str(h['h_building']) == str(h['h_building']):
                print('asdf')
                return h['h_id']
            else:
                continue

    def street_search_type(self, name):
        streets = self.session.get('https://partnerweb.beeline.ru/ngapi/find_by_city_and_street/'
                                   '?cityPattern=&streetPattern=' + str(encode(name))).json()
        addresses = []
        for street in streets:
            cities = list([int(id) for id in os.getenv('CITIES_ID').split(',')])
            if street['s_city'] in cities:
                addresses.append({'city': street['city'], 'street_name': street['street_name'], 's_id': street['s_id']})
        return addresses

    def get_full_house_info(self, id):
        return self.session.get(f'https://partnerweb.beeline.ru/ngapi/house/{id}/').json()

class Schedule(Address):

    def schedule_interval_by_day(self, ticket_id, year, month, day, house_id=False):
        ar_id = ''
        free_times = {}
        if ticket_id:
            ar_id = self.get_num_house_by_id(ticket_id)['num_house']
        if house_id:
            ar_id = self.get_house_info(house_id)['h_dealer']['ar_id']
        schedule_session = self.session.get(f'https://partnerweb.beeline.ru/restapi/schedule/get_day_schedule/{ar_id}?'
                                            + urllib.parse.urlencode({'day': str(day), 'month': str(month),
                                                                      'year': str(year)})).json()
        free_time = schedule_session['data']['classic_schedule']
        time_intervals = []
        for time in free_time:
            time_intervals.append(
                {
                    'cell' : time['cell'],
                    'intbegin' : time['intbegin'],
                    'intend' : time['intend'],
                    'count_free_cells' : len(time['free_cells']),
                    'convenient_time' : formate_date_schedule(time['intbegin'])
                }
            )
        return time_intervals

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

    def get_mobile_presets(self, city_id, house_id):
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

class NewDesign(Basket, TicketParser):

    def ticket_info(self, id):
        attr = self.session.get(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}').json()
        ticket = self.ticket_instance_info(attr)
        return ticket


    def assync_get_ticket(self, urls):
        ticket_dict = {}
        rc = [grequests.get(url, session=self.session) for url in urls]
        for index, response in enumerate(grequests.map(rc)):
            ticket_dict[index] = response.json()
        return ticket_dict

    def search_by(self, phone, city='', dateFrom=False, dateTo=False, number='', shop='', status='', pages=None):
        tickets = self.retrive_tickets(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number, phone=phone,
                                       shop=shop, status=status, pages=pages)
        return tickets

    def create_ticket(self, house_id, flat, client_name, client_patrony, client_surname, phone_number_1, id,service_type,vpdn,
                      need_schedule=False):
        st = service_type.lower().replace('is_', '') + ('_service')
        data = {"house_id":house_id,"flat":flat,"create_contract":1,"client_name":client_name,
                "client_patrony":client_patrony,
                "client_surname":client_surname,
                "phone_number_1":phone_number_1,
                "sms_warnto_1" : 1,
                st:id,
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
    def assigned_tickets_detailed(self, tickets):
        asig_ts, asig_ts_today, urls = [], 0, []
        for ticket in tickets:
            try:
                if ((ticket.type_id == 286 or ticket.type_id == 250)
                        and (ticket.status_id == 157 or ticket.status_id == 132
                        or ticket.status_id == 154 or ticket.status_id == 128)) \
                        and ticket.ticket_paired_info.allow_schedule == False \
                        and ticket.ticket_paired_info.allow_change_status == True:
                    urls.append(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{ticket.id}')
            except:
                continue
        parse_tickets = self.assync_get_ticket(urls)
        a_t = [self.ticket_instance_info(value) for key, value in parse_tickets.items()]
        filter_satelit = []
        for ticket in a_t:
            ticket.ticket_paired_info = list([i for i in tickets if i.id == ticket.ticket_paired])[0]
            as_t = list([c['date'] for c in ticket.comments if find_asssigned_date(c['text'])])
            ticket.assigned_date = as_t[0] if as_t else None
            if dmYHM_to_date(ticket.assigned_date) == dt.now().date():
                asig_ts_today += 1
            asig_ts.append(ticket)
        return asig_ts, asig_ts_today

    @system.my_timer
    def assigned_tickets(self, tickets):
        asig_ts, asig_ts_today = [], 0
        for ticket in tickets:
            try:
                if ((ticket.type_id == 286 or ticket.type_id == 250)
                        and (ticket.status_id == 157 or ticket.status_id == 132
                        or ticket.status_id == 154 or ticket.status_id == 128)) \
                        and ticket.ticket_paired_info.allow_schedule == False \
                        and ticket.ticket_paired_info.allow_change_status == True:
                    asig_ts.append(ticket)
            except:
                continue
        return asig_ts, asig_ts_today

    @system.my_timer
    def switched_tickets(self, tickets):
        sw_ts, sw_ts_today = [], 0
        last, cur_month, cur_year = last_day_current_month()
        for t in tickets:
            if t.type_id == 286 or t.type_id == 250:
                try:
                    if t.ticket_paired_info.status_id == 4\
                            and (t.status_id == 154 or t.status_id == 128)\
                            and t.call_time != None and \
                            (date(cur_year, cur_month, 1) <= dmYHM_to_date(t.ticket_paired_info.call_time) <= date(cur_year, cur_month, last)):
                        sw_ts_today = self.count_switched(sw_ts_today, t)
                        sw_ts.append(t)
                except:
                    continue
        return sw_ts, sw_ts_today

    @staticmethod
    def count_switched(sw_ts_today, t):
        sw_ts_today += 1 if dmYHM_to_date(t.ticket_paired_info.call_time) == today() else 0
        return sw_ts_today

    @system.my_timer
    def retrive_tickets(self, city='', dateFrom=False, dateTo=False, number='', phone='',
                        shop='', status='', pages=40):
        ticket_dict, tickets = self.async_base_tickets(city, dateFrom, dateTo, number, pages, phone, shop, status)
        for key, item in ticket_dict.items():
            for attr in item:
                attr['comments'] = attr.get('comments')
                attr['services'] = attr.get('services')
                attr['shop'] = attr.get('shop')
                attr['shop_id'] = attr.get('shop_id')
                phone1, phone2, phone3 = get_phone123(attr)
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
                                type=attr['type'], type_id=attr['type_id'], status_id=attr['status_id'])
                tickets.append(ticket)
        all_paired_tickets = []
        for ticket in tickets:
            if ticket.ticket_paired:
                ticket.ticket_paired_info = self.check_paired_ticket_info(ticket.ticket_paired, tickets)
                all_paired_tickets.append(ticket)
        self.tickets = all_paired_tickets
        return all_paired_tickets

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

    @staticmethod
    def call_today_tickets(tickets):
        call_ts_today = []
        for t in tickets:
            try:
                time_value = dmYHM_to_date(t.ticket_paired_info.call_time)
                date_start = dmY_to_date(t.date)
            except:
                print(t.number)
                continue
            try:
                if (t.ticket_paired_info.status_id in [16, 21, 123, 122, 76]) and (time_value == dt(1000, 1, 1) or time_value <= today() or None):
                        call_ts_today.append(t)
                        t.is_expired = True if date_start + timedelta(days=30) < datetime.date.today() else None
                        print(t.is_expired)
            except Exception as e:
                print(e)
        return call_ts_today

    @staticmethod
    def count_created_today(tickets):
        count = 0
        for ticket in tickets:
            try:
                count += 1 if (dmY_to_date(ticket.date) == today()) else 0
            except:
                continue
        return count

    def three_month_tickets(self):
        tickets = self.remove_garbage_tickets(self.retrive_tickets())
        assigned_tickets, assigned_tickets_today = self.assigned_tickets(tickets)
        call_today_tickets = self.call_today_tickets(tickets)
        switched_tickets, switched_on_tickets_today = self.switched_tickets(tickets)
        created_today_tickets = self.count_created_today(tickets)
        return assigned_tickets, assigned_tickets_today, call_today_tickets, switched_tickets, \
               switched_on_tickets_today, created_today_tickets, tickets

    def remove_garbage_tickets(self, tickets):
        return [t for t in tickets if t.status != 'Мусор']

    def global_search(self):
        clear_tickets = []
        for ticket in self.retrive_tickets():
            if (ticket.type_id == 286 or ticket.type_id == 250):
                clear_tickets.append(ticket)
        return clear_tickets

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


    def change_ticket(self, id, timer, comment='', status_id=21):
        url_status = f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{id}'
        comment = '; '.join(comment) if isinstance(comment, list) else comment
        if status_id == '2028':
            data_timer = {"status_id": 21, "call_time": '31.12.2028 00:00', "comment": comment}
            return self.session.post(url_status, data_timer).json()
        if status_id == '16':
            data_timer = {"status_id": 16, "call_time": '31.12.2028 00:00', "comment": comment}
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

    def get_ctn_info(self, ctn):
        return self.session.\
            get(f'https://partnerweb.beeline.ru/restapi/convergent/check_ctn/{ctn}?action=upsell').json()

    # not working
    def get_switch_lite_info(self, ctn):
        self.session.get('https://partnerweb.beeline.ru/contract_lite/ctn/')
        self.session.headers['sec-fetch-user'] = '?1'
        self.session.headers['cookie'] = 'sessionid=zxs7i82iojbtd4en5mpuhm8worw4b5ey'
        data = self.session.post('https://partnerweb.beeline.ru/contract_lite/ctn/', f'ctn_field={ctn}')
        return data

    def change_phone_info(self, ticket_id, data):
        self.session.headers['sec-fetch-dest'] = 'empty'
        self.session.headers['sec-fetch-mode'] = 'cors'
        self.session.headers['sec-fetch-site'] = 'same-origin'
        self.session.headers['accept'] = 'application/json, text/plain, */*'
        self.session.headers['accept-encoding'] = 'gzip, deflate, br'
        self.session.headers['accept-language'] = 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-GB;q=0.6'
        self.session.headers['content-type'] = 'application/json;charset=UTF-8'
        phones = json.loads(data)
        return self.session.post(f'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{ticket_id}',
                                 json.dumps(phones)).json()
    def assign_ticket(self,data):
        self.session.headers['sec-fetch-dest'] = 'empty'
        self.session.headers['sec-fetch-mode'] = 'cors'
        self.session.headers['sec-fetch-site'] = 'same-origin'
        self.session.headers['accept'] = 'application/json, text/plain, */*'
        self.session.headers['accept-encoding'] = 'gzip, deflate, br'
        self.session.headers['accept-language'] = 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-GB;q=0.6'
        self.session.headers['content-type'] = 'application/json;charset=UTF-8'
        data = json.loads(data)
        return self.session.post(f'https://partnerweb.beeline.ru/restapi/schedule/do_schedule',
                                 json.dumps(data)).json()


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
        if isinstance(auth, list):
            auth = NewDesign(auth[0],auth[1],auth[2])
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