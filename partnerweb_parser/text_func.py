import re
import urllib.parse


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


def phone9(mystr):
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

def get_phone123(attr):
    phone1 = attr['phones'][0]['phone'] if len(attr['phones']) else ''
    phone2 = attr['phones'][1]['phone'] if 1 < len(attr['phones']) else ''
    phone3 = attr['phones'][2]['phone'] if 2 < len(attr['phones']) else ''
    return phone1, phone2, phone3