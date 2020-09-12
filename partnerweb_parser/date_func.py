import calendar
import datetime
from datetime import datetime as dt
import pytz
moscow = pytz.timezone('Europe/Moscow')

def current_date():
    now_date = datetime.date.today()  # Текущая дата (без времени)
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


def url_formate_date(date):
    return date.strftime("%d.%m.%Y")


def formate_date_schedule(str_date):
    return datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S+00:00').strftime('%H:%M')


def delta_current_month(date_first, date_second):
    date_second = date_second - datetime.timedelta(days=30)
    date_first = date_first - datetime.timedelta(days=30)
    return date_first, date_second


def range_current_month():
    now_date = datetime.date.today()
    date_first = now_date - datetime.timedelta(days=30)
    date_second = now_date + datetime.timedelta(days=1)
    return date_first, date_second


def current_year_date():
    now_date = datetime.date.today()
    date_first = url_formate_date(now_date - datetime.timedelta(days=365))
    date_second = url_formate_date(now_date + datetime.timedelta(days=1))
    return date_first, date_second

def dmYHM_to_date(ticket_call_time):
    return dt.strptime(ticket_call_time, "%d.%m.%Y %H:%M").date() if ticket_call_time else dt(1000, 1, 1)

def dmYHM_to_datetime(ticket_call_time):
    d = dt.strptime(ticket_call_time, "%d.%m.%Y %H:%M") if ticket_call_time else dt(1000, 1, 1)
    return moscow.localize(d)

def dmY_to_date(ticket_call_time):
    return dt.strptime(ticket_call_time, "%d.%m.%Y").date()

def today():
    return datetime.date.today()
def convert_utc_string(date):
    format = '%Y-%m-%dT%H:%M:%S%z'
    return datetime.datetime.strptime(date, format)