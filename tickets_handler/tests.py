from django.test import TestCase, SimpleTestCase
from partnerweb_parser.manager import NewDesign
import unittest
import os
# Create your tests here.
from django.urls import reverse


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

