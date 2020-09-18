import time

from django.core.cache import cache
from django.test import TestCase, SimpleTestCase, Client
from partnerweb_parser.manager import NewDesign
import unittest
import os
# Create your tests here.
from django.urls import reverse
from urllib.parse import urlencode


class LoginPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('login')
        self.response = self.client.get(url)
        self.sell_code = os.environ.get('SELL_CODE')
        self.operator = os.environ.get('A_OPERATOR')
        self.password = os.environ.get('A_PASS')
        self.auth = NewDesign(self.sell_code,self.operator,self.password)

    def test_login_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_auth(self):
        auth_a = self.auth.session.get('https://partnerweb.beeline.ru/restapi/auth/current-user/')
        self.assertEqual(auth_a.json()['data']['login'], '9052933642')
        self.assertEqual(auth_a.json()['data']['type'], 4)
        self.assertEqual(auth_a.json()['data']['convergence'], True)


class MainPageTests(TestCase):

    def setUp(self):
        self.url = reverse('main_page_tickets')
        self.response = self.client.get(self.url)
        self.sell_code = os.environ.get('SELL_CODE')
        self.operator = os.environ.get('A_OPERATOR')
        self.password = os.environ.get('A_PASS')
        self.auth = NewDesign(self.sell_code,self.operator,self.password)

    def test_access_without_auth(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse('login'))

    def test_access_with_auth(self):
        login_url = reverse('login')
        data = urlencode({"operator":self.operator, "password": self.password})
        response = self.client.post(login_url, data, content_type="application/x-www-form-urlencoded")
        if cache.get('supervisors_tickets'):
            self.assertRedirects(response, reverse('main_page_rapid'))
        else:
            self.assertRedirects(response, reverse('main_page_tickets'))

    def test_load_non_rapid_version(self):
        login_url = reverse('login')
        data = urlencode({"operator": self.operator, "password": self.password})
        self.client.post(login_url, data, content_type="application/x-www-form-urlencoded")
        start = time.time()
        response = self.client.get(reverse('main_page_tickets'))
        end = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end-start, 60)
        self.assertContains(response, 'Назначенные в график')
        self.assertContains(response, 'Перезвоны на сегодня')
        self.assertContains(response, 'Подключенные')

class DetailTicketInfoTests(TestCase):

    def setUp(self):
        self.url = reverse('ticket_info', kwargs={"id" : 109706332})
        self.response = self.client.get(self.url)
        self.sell_code = os.environ.get('SELL_CODE')
        self.operator = os.environ.get('A_OPERATOR')
        self.password = os.environ.get('A_PASS')
        self.auth = NewDesign(self.sell_code,self.operator,self.password)

    def test_access_without_auth(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse('login'))

    def test_load_auth_info(self):
        login_url = reverse('login')
        data = urlencode({"operator": self.operator, "password": self.password})
        self.client.post(login_url, data, content_type="application/x-www-form-urlencoded")
        start = time.time()
        response = self.client.get(self.url)
        end = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end-start, 30)
        self.assertContains(response, 'фываыавпфыва')
        self.assertContains(response, '9111111111')
        self.assertNotContains(response, 'Ошибка сателитной заявки')
