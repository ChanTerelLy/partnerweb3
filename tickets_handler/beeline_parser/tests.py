import requests
import unittest
import tracemalloc
from tickets_handler.beeline_parser import manager
import os


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.auth_supervisor = manager.Auth(os.getenv('SELL_CODE'),os.getenv('S_OPERATOR'),os.getenv('S_PASSWORD'))
        self.auth_agent = manager.Auth(os.getenv('SELL_CODE'),os.getenv('A_OPERATOR'),os.getenv('A_PASSWORD'))

    def test_ping_partnerweb(self):
        auth = requests.session().get('https://partnerweb.beeline.ru/#!/').status_code
        self.assertEqual(auth, 200)

    def test_auth(self):
        auth_s = self.auth_supervisor.session.get('https://partnerweb.beeline.ru/restapi/auth/current-user/')
        auth_a = self.auth_agent.session.get('https://partnerweb.beeline.ru/restapi/auth/current-user/')
        auth_a.encoding, auth_s.encoding = 'utf-8', 'utf-8'
        self.assertEqual(auth_s.json()['data']['login'], os.getenv('S_OPERATOR'))
        self.assertEqual(auth_a.json()['data']['login'], os.getenv('A_OPERATOR'))
        self.assertEqual(auth_s.json()['data']['type'], 3)
        self.assertEqual(auth_a.json()['data']['type'], 4)
        self.assertEqual(auth_s.json()['data']['convergence'], 0)
        self.assertEqual(auth_a.json()['data']['convergence'], True)


class TestNewDesign(unittest.TestCase):

    def setUp(self):
        self.ND = manager.NewDesign(os.getenv('SELL_CODE'),os.getenv('A_OPERATOR'),os.getenv('A_PASSWORD'))

    def test_define_calling_tickets(self):
        self.assertTrue(self.ND.define_call_ts('Позвонить клиенту 15.09.2019 00:00'))

    def test_definde_satellit_ticket(self):
        self.assertTrue(self.ND.definde_satellit_ticket('Закрыта 15.09.2019 00:00'))

if __name__ == '__main__':
    unittest.main()