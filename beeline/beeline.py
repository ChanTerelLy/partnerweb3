import requests
import lxml.html
import datetime
import calendar
from openpyxl import Workbook
import re
import json
import urllib.parse
import time


def find_asssigned_date(comments):
    pattern = r'Заявка назначена в график на'
    if re.search(pattern, comments):
        return True
    else:
        return False


def find_switched_on(comments):
    pattern = r'клиент подключен'
    if re.search(pattern, comments):
        return True
    else:
        return False


def find_dns(address):
    pattern = r'^Архангельск, пр-кт. Московский, д. 5[524][к]?[23]?|' \
              r'^Архангельск, ул. Мещерского, д. 38|' \
              r'^Архангельск, ул. Победы, д. 11[642]к?[2]?|' \
              r'^Архангельск, ул. Вологодская, д. 30|' \
              r'^Архангельск, ул. Воронина, д. 15|' \
              r'^Архангельск, ул. Тимме, д. 2к[24]|' \
              r'^Архангельск, ул. Карпогорская, д. 32|' \
              r'^Архангельск, ул. 23 гвардейской дивизии, д. 4|' \
              r'^Архангельск, ул. Стрелковая, д. 2[75]|' \
			  r'^Архангельск, ул. Школьная, д. 8[46][к]?[23]?|' \
			  r'^Архангельск, ул. Суворова, д. 11к2|' \
			  r'^Архангельск, ул. Овощная, д. 21'
    if re.match(pattern, address):
        dns = 'ДНС'
    else:
        dns = ''
    return dns


def numers(mystr):
    if mystr != None:
        mystr = re.sub(r"[-]", "", mystr)
        mystr = mystr.replace(' 8', '')
        mystr = mystr[1:]
        mystr = mystr.split(',')
    else:
        mystr = ['', '', '']
    return mystr


def encode(d):
    return urllib.parse.quote(str(d).encode('utf8'))


def current_date():
    now_date = datetime.date.today()  # Текущая дата (без времени)
    now_time = datetime.datetime.now()  # Текущая дата со временем
    cur_year = now_date.year  # Год текущий
    cur_month = now_date.month  # Месяц текущий
    cur_day = now_date.day  # День текущий
    return cur_day, cur_month, cur_year


def last_day_current_month():
    now_date = datetime.date.today()
    cur_year = now_date.year  # Год текущий
    cur_month = now_date.month  # Месяц текущий
    last_day = calendar.monthrange(cur_year, cur_month)[1]
    return last_day, cur_month, cur_year


def formate_date(date):
    return date.strftime("%d.%m.%Y")


def formate_date_schedule(str_date):
    return datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S+00:00').strftime('%H:%M')


def filter_previous_month(date_first, date_second):
    date_second = date_second - datetime.timedelta(days=30)
    date_first = date_first - datetime.timedelta(days=30)
    return date_first, date_second


def current_moth_date():
    now_date = datetime.date.today()
    date_first = now_date - datetime.timedelta(days=30)
    date_second = now_date + datetime.timedelta(days=1)
    return date_first, date_second


def current_year_date():
    now_date = datetime.date.today()
    date_first = formate_date(now_date - datetime.timedelta(days=365))
    date_second = formate_date(now_date + datetime.timedelta(days=1))
    return date_first, date_second


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
        self.session.post('https://partnerweb.beeline.ru', self.data, headers=self.headers)


class Ticket:

    def __init__(self, address='', address_id='', allow_change_status='', allow_schedule='', call_time=None,
                 comments='',
                 date='', id='', name='', number='', operator='', phones='', services='', shop='', shop_id='',
                 status='',
                 ticket_paired='', type='', type_id='', phone1='', phone2='', phone3='', comment1='', comment2='',
                 comment3='', assigned_date=None, dns=''):
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

    def __repr__(self):
        return str(self.__dict__)


class OldDesign(Auth):

    def ticket_info(self, id):
        g = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/'
                             + str(id)).json()
        ticket = Ticket(address=g['address'], address_id=g['address_id'],
                        allow_change_status=g['allow_change_status'],
                        allow_schedule=g['allow_schedule'], call_time=g['call_time'], comments=g['comments'],
                        date=g['date'], id=g['id'], name=g['name'], number=g['number'], operator=g['operator'],
                        phones=g['phones'],
                        services=g['services'], shop=g['shop'], shop_id=g['shop_id'], status=g['status'],
                        ticket_paired=g['ticket_paired'], type=g['type'], type_id=g['type_id'])
        return ticket

    def get_comments(self, id):
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

    def schedule(self, ticket_id, day):
        address_session = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/api/ticket/'
                                           + str(ticket_id) + '?rnduncache=5466&')
        dic = address_session.json()
        cur_day, cur_month, cur_year = current_date()
        num_house = dic['t_address']['h']['h_dealer']['id']
        schedule_session = self.session.get('https://partnerweb.beeline.ru/restapi/schedule/get_day_schedule/'
                                            + str(num_house) + '?' + str(urllib.parse.urlencode({'day': str(day),
                                                                                                 'month': str(
                                                                                                     cur_month),
                                                                                                 'year': str(
                                                                                                     cur_year)}))).json()
        get_free_time = schedule_session['data']['classic_schedule']
        for i in get_free_time:
            print(formate_date_schedule(i['intbegin']), '-', formate_date_schedule(i['intend']))
        return num_house

    def count_created_today(self, table):
        created_today = 0
        for i in table:
            if i[2].text == 'Заявка на подключение':
                if datetime.datetime.strptime(i[4].text, '%d.%m.%Y').date() == datetime.datetime.now().date():
                    created_today = created_today + 1
        return created_today

    def assigned_tickets(self, table):
        assigned_tickets = []
        assigned_today = 0
        for i in table:
            if i[2].text == 'Заявка на подключение' and i[9].text == 'Назначено в график':
                full_info = self.ticket_info(i[0][0].get('id'))  # id ticket
                # for comment in full_info.comments:
                #     if find_asssigned_date(comment['text']):
                #         assigned_date = comment['date']
                #         assigned_today = assigned_today = assigned_today + 1 if (
                #                     datetime.datetime.strptime(assigned_date, '%d.%m.%Y %H:%M').date() ==
                #                     datetime.datetime.now().date()) else assigned_today
                #         break
                phone2 = numers(i[8].text)[1] if 1 < len(numers(i[8].text)) else ''
                phone3 = numers(i[8].text)[2] if 2 < len(numers(i[8].text)) else ''
                ticket = Ticket(number=i[3].text, name=i[6].text, address=i[7].text,
                                phone1=numers(i[8].text)[0],
                                phone2=phone2,
                                phone3=phone3,
                                status=i[9].text,
                                call_time=i[10].text, operator=i[11].text,
                                id=i[0][0].get('id'), assigned_date='', dns=find_dns(i[7].text))
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
                    timer = datetime.datetime.strptime(i[10].text, '%d.%m.%Y %H.%M').date()
                except:
                    continue
                if timer <= datetime.datetime.now().date() or None:
                    timer = datetime.datetime.strptime(i[10].text, '%d.%m.%Y %H.%M')
                    phone2 = numers(i[8].text)[1] if 1 < len(numers(i[8].text)) else ''
                    phone3 = numers(i[8].text)[2] if 2 < len(numers(i[8].text)) else ''
                    ticket = Ticket(number=i[3].text, name=i[6].text, address=i[7].text,
                                    phone1=numers(i[8].text)[0],
                                    phone2=phone2,
                                    phone3=phone3,
                                    status=i[9].text, call_time=timer, operator=i[11].text,
                                    id=i[0][0].get('id'))
                    call_today_tickets.append(ticket)
        return call_today_tickets

    def swithed_on_tickets(self, table):
        switched_tickets = []
        swithed_on_today = 0
        for i in table:
            if i[2].text == 'Заявка на подключение' and i[9].text == 'Подключен':
                timer = ''
                try:
                    timer = datetime.datetime.strptime(i[10].text, '%d.%m.%Y %H.%M').date()
                except:
                    continue
                last, cur_month, cur_year = last_day_current_month()  # filter for current month
                if (timer <= datetime.date(cur_year, cur_month, last)) and (
                        timer >= datetime.date(cur_year, cur_month, 1)):
                    swithed_on_today = swithed_on_today = swithed_on_today + 1 if timer == datetime.datetime.now().date() else swithed_on_today
                    phone2 = numers(i[8].text)[1] if 1 < len(numers(i[8].text)) else ''
                    phone3 = numers(i[8].text)[2] if 2 < len(numers(i[8].text)) else ''
                    ticket = Ticket(number=i[3].text, name=i[6].text, address=i[7].text,
                                    phone1=numers(i[8].text)[0],
                                    phone2=phone2,
                                    phone3=phone3,
                                    status=i[9].text, call_time=timer, operator=i[11].text,
                                    id=i[0][0].get('id'), dns=find_dns(i[7].text))
                    switched_tickets.append(ticket)
        return switched_tickets, swithed_on_today

    def three_month_tickets(self):
        date_first, date_second = current_moth_date()
        assigned_tickets = []
        assigned_tickets_today = 0
        call_today_tickets = []
        switched_tickets = []
        switched_on_tickets_today = 0
        created_today_tickets = 0
        for month in range(2):
            data = dict(date_start=str(formate_date(date_first)), date_end=str(formate_date(date_second)))
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
            date_first, date_second = filter_previous_month(date_first, date_second)
        return assigned_tickets, assigned_tickets_today, call_today_tickets, switched_tickets, switched_on_tickets_today, created_today_tickets

    def change_ticket(self, id, timer, comment, phone):
        url_status = 'https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/{}'.format(str(id))
        data_timer = {"status_id":21,"call_time":timer, "comment":comment}
        self.session.post(url_status, data_timer)


    def months_report(self, num_months):
        book = Workbook()
        sheet = book.active
        row = '2'  # number row of excel
        date_first, date_second = current_moth_date()
        for x in range(num_months):
            data = dict(date_start=str(formate_date(date_first)), date_end=str(formate_date(date_second)))
            filter_page = self.session.post('https://partnerweb.beeline.ru/main/', data)
            doc = lxml.html.fromstring(filter_page.content)
            table = doc.cssselect('table.tablesorter')[0][1]
            for i in table:
                if i[2].text == 'Заявка на подключение':
                    sheet['D' + row] = i[3].text  # номер заявки
                    sheet['A' + row] = i[6].text  # фио
                    sheet['B' + row] = i[7].text  # адрес
                    sheet['C' + row] = numers(str(i[8].text))  # номер телефона
                    sheet['E' + row] = i[9].text  # статус
                    sheet['F' + row] = i[10].text  # таймер
                    sheet['G' + row] = i[11].text  # сотрудник
                    # sheet['H' + str(g)] = get_comments(str(i[3].text))
                    row = str(int(row) + 1)
            date_first, date_second = filter_previous_month(date_first, date_second)
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
        date_first, date_second = current_moth_date()
        tickets = []
        for month in range(4):
            data = dict(date_start=str(formate_date(date_first)), date_end=str(formate_date(date_second)))
            filter_page = self.session.post('https://partnerweb.beeline.ru/main/', data)
            doc = lxml.html.fromstring(filter_page.content)
            table = doc.cssselect('table.tablesorter')[0][1]
            tickets = []
            for i in table:
                timer = ''
                try:
                    timer = datetime.datetime.strptime(i[10].text, '%d.%m.%Y %H.%M').date()
                except:
                    continue
                phone2 = numers(i[8].text)[1] if 1 < len(numers(i[8].text)) else ''
                phone3 = numers(i[8].text)[2] if 2 < len(numers(i[8].text)) else ''
                ticket = Ticket(type=i[1].text, date=i[4].text, number=i[3].text, name=i[6].text, address=i[7].text,
                                phone1=numers(i[8].text)[0],
                                phone2=phone2,
                                phone3=phone3,
                                status=i[9].text, call_time=timer, operator=i[11].text,
                                id=i[0][0].get('id'), dns=find_dns(i[7].text))
                tickets.append(ticket)
        return tickets


class NewDesign(OldDesign):

    def get_gp(self, num_houme, all=False):
        gp_session = Auth.session.get('https://partnerweb.beeline.ru/restapi/hd/global_problems_on_house/'
                                      + str(num_houme) + '?rnd=1544255167014').json()
        areas = []
        houses = []
        for i in gp_session['data']['areas']:
            areas.append(i['description'])
        for i in gp_session['data']['houses']:
            houses.append(i['description'])
        return areas, houses

    def ticket_info(self, id):
        g = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/ticket_popup/'
                             + str(id)).json()
        ticket = Ticket(address=g['address'], address_id=g['address_id'],
                        allow_change_status=g['allow_change_status'],
                        allow_schedule=g['allow_schedule'], call_time=g['call_time'], comments=g['comments'],
                        date=g['date'], id=g['id'], name=g['name'], number=g['number'], operator=g['operator'],
                        phones=g['phones'],
                        services=g['services'], shop=g['shop'], shop_id=g['shop_id'], status=g['status'],
                        ticket_paired=g['ticket_paired'], type=g['type'], type_id=g['type_id'])
        return ticket

    def choose_house(self, name, id_street=False, ):
        streets = self.session.get('https://partnerweb.beeline.ru/ngapi/find_by_city_and_street/'
                                   '?cityPattern=&streetPattern=' + str(encode(name))).json()
        for street in streets:
            if street['s_city'] == 69 or street['s_city'] == 241 or street['s_city'] == 86:
                print(street['city'], street['street_name'], street['s_id'])
        id_street = input("Введите id улицы")
        homes_json = self.session.get(
            'https://partnerweb.beeline.ru/ngapi/find_by_house/' + str(id_street) + '/').json()
        for street in homes_json:
            if street['h_status'] == "connected":
                h_list = street['house_address'].split(',')
                print(h_list[2], street['h_id'])
        num_house = input('Введите id дома:')
        return num_house

    def fraud_check(self, flat=0, num_house=0):
        flat_session = self.session.get(
            'https://partnerweb.beeline.ru/restapi/tickets/checkfraud/' + str(num_house) + '/' + str(flat)).json()
        if flat_session['metadata']['status'] == 40002:
            print(flat_session['metadata']['message'])
        else:
            print('ОК!')

    def assigned_tickets(self, tickets):
        assigned_tickets_today = 0
        assigned_tickets = []
        for ticket in tickets:
            if ticket.type_id == 1 and ticket.allow_schedule == False and ticket.allow_change_status == True:
                for comment in self.ticket_info(ticket.id).comments:
                    if find_asssigned_date(comment['text']):
                        if datetime.datetime.strptime(comment['date'], '%d.%m.%Y %H:%M').date() == datetime.datetime.now().date():
                            assigned_tickets_today =+1
                        break
                assigned_tickets.append(ticket)
        return assigned_tickets, assigned_tickets_today

    def search_phone(self, phone, city='', dateFrom=False, dateTo=False, number='',
                     shop='', status='', pages=None):
        tickets = self.tickets(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number, phone=phone,
                               shop='', status=status, pages=pages)
        return tickets

    def search_number(self, number, phone='', city='', dateFrom=False, dateTo=False,
                      shop='', status='', pages=None):
        tickets = self.tickets(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number, phone=phone,
                               shop='', status=status, pages=pages)
        return tickets

    def call_for_today(self, city='', dateFrom=False, dateTo=False, number='', phone='',
                       shop='', pages=1):
        station = (7, 9, 1, 11)  # ждем звонка , позвонить клиенту и позвонить срочно, новая, резерв
        tickets = []
        for i in station:
            status = i
            if not dateFrom and not dateTo:
                dateFrom, dateTo = current_year_date()
            ticket_dict = {}
            for pageCount in range(1, pages + 1):
                url = urllib.parse.urlencode(
                    dict(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number, page=pageCount,
                         phone=phone, shop=shop, status=status))
                new_design_ticket_info = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/?'
                                                          + url).json()
                if len(new_design_ticket_info) == 0:
                    break
                else:
                    ticket_dict[pageCount] = new_design_ticket_info
            for i in range(1, len(ticket_dict) + 1):
                for g in ticket_dict[i]:
                    if g['type_id'] == 1:
                        try:
                            timer = datetime.datetime.strptime(g['call_time'], '%d.%m.%Y %H:%M').date()
                        except:
                            continue
                        if timer <= datetime.datetime.now().date() or None:
                            g['comments'] = g.get('comments')
                            g['services'] = g.get('services')
                            g['shop'] = g.get('shop')
                            g['shop_id'] = g.get('shop_id')
                            ticket = Ticket(address=g['address'], address_id=g['address_id'],
                                            allow_change_status=g['allow_change_status'],
                                            allow_schedule=g['allow_schedule'], call_time=g['call_time'],
                                            comments=g['comments'],
                                            date=g['date'], id=g['id'], name=g['name'], number=g['number'],
                                            operator=g['operator'],
                                            phones=g['phones'],
                                            services=g['services'], shop=g['shop'], shop_id=g['shop_id'],
                                            status=g['status'],
                                            ticket_paired=g['ticket_paired'], type=g['type'], type_id=g['type_id'])
                            tickets.append(ticket)
        return tickets

    def tickets(self, city='', dateFrom=False, dateTo=False, number='', phone='',
                shop='', status='', pages=6):
        ticket_dict, tickets = self.base_ticket_info(city, dateFrom, dateTo, number, pages, phone, shop, status)
        for i in range(1, len(ticket_dict) + 1):
            for g in ticket_dict[i]:
                g['comments'] = g.get('comments')
                g['services'] = g.get('services')
                g['shop'] = g.get('shop')
                g['shop_id'] = g.get('shop_id')
                ticket = Ticket(address=g['address'], address_id=g['address_id'],
                                allow_change_status=g['allow_change_status'],
                                allow_schedule=g['allow_schedule'], call_time=g['call_time'], comments=g['comments'],
                                date=g['date'], id=g['id'], name=g['name'], number=g['number'], operator=g['operator'],
                                phones=g['phones'],
                                services=g['services'], shop=g['shop'], shop_id=g['shop_id'], status=g['status'],
                                ticket_paired=g['ticket_paired'], type=g['type'], type_id=g['type_id'])
                tickets.append(ticket)
        return tickets

    def base_ticket_info(self, city, dateFrom, dateTo, number, pages, phone, shop, status):
        if not dateFrom and not dateTo:
            dateFrom, dateTo = current_year_date()
        ticket_dict = {}
        tickets = []
        for pageCount in range(1, pages + 1):
            url = urllib.parse.urlencode(
                dict(city=city, dateFrom=dateFrom, dateTo=dateTo, number=number, page=pageCount,
                     phone=phone, shop=shop, status=status))
            new_design_ticket_info = self.session.get('https://partnerweb.beeline.ru/restapi/tickets/?'
                                                      + url).json()
            if len(new_design_ticket_info) == 0:
                break
            else:
                ticket_dict[pageCount] = new_design_ticket_info
        return ticket_dict, tickets

    def create_ticket(self, house_id, flat, client_name, client_patrony, client_surname, phone_number_1,
                      need_schedule=False):
        data = {"house_id": house_id, "flat": flat, "create_contract": 1, "client_name": client_name,
                "client_patrony": client_patrony, "client_surname": client_surname, "phone_number_1": phone_number_1,
                "sms_warnto_1": 1, "service_type": "typical", "simple_vpdn": "M130990",
                "basket": {"MAIN": {"VPDN": {"S_ID": "M130990"}}}, "need_schedule": need_schedule}
        self.session.get('https://partnerweb.beeline.ru/ngapp#!/newaddress/connect_ticket/house_id/446187')
        self.session.headers["origin"] = "https://partnerweb.beeline.ru"
        self.session.headers["accept-language"] = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        self.session.headers["x-requested-with"] = "XMLHttpRequest"
        self.session.headers['content-type'] = 'application/json'
        self.session.headers[
            "http_referer"] = "https://partnerweb.beeline.ru/ngapp#!/newaddress/connect_ticket/house_id/450541"
        send_ticket = self.session.post('https://partnerweb.beeline.ru/restapi/tickets/', json.dumps(data))

    def three_month_tickets(self):
        assigned_tickets = []
        assigned_tickets_today = 0
        call_today_tickets = []
        switched_tickets = []
        switched_on_tickets_today = 0
        created_today_tickets = 0
        tickets = self.tickets()

        return assigned_tickets, assigned_tickets_today, call_today_tickets, switched_tickets, switched_on_tickets_today, created_today_tickets



if __name__ == "__main__":
    start = time.time()
    #auth = NewDesign('G800-37', 'Корытов_Р.В.', 'roma456')
    auth = OldDesign('G800-37', 'Корытов_Р.В.', 'roma456')
    print(auth.three_month_tickets())
    end = time.time()
    print(end - start)
