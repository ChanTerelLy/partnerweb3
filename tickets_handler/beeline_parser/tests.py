import unittest
from tickets_handler.beeline_parser import manager

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.auth_supervisor = manager.Auth('G800-37', 'Хоменко', '1604')
        self.auth_agent = manager.Auth('G800-37', '9642907288', 'roma456')

    # def test_ping_partnerweb(self):
    #     auth = requests.session().get('https://partnerweb.beeline.ru/#!/').status_code
    #     self.assertEqual(auth, 200)

    def test_auth(self):
        auth_s = self.auth_supervisor.session.get('https://partnerweb.beeline.ru/restapi/auth/current-user/')
        auth_a = self.auth_agent.session.get('https://partnerweb.beeline.ru/restapi/auth/current-user/')
        auth_a.encoding, auth_s.encoding = 'utf-8', 'utf-8'
        self.assertEqual(auth_s.json()['data']['login'], 'Хоменко')
        self.assertEqual(auth_a.json()['data']['login'], '9642907288')
        self.assertEqual(auth_s.json()['data']['type'], 3)
        self.assertEqual(auth_a.json()['data']['type'], 4)
        self.assertEqual(auth_s.json()['data']['convergence'], 0)
        self.assertEqual(auth_a.json()['data']['convergence'], True)




class TestNewDesign(unittest.TestCase):

    def setUp(self):
        self.ND = manager.NewDesign('G800-37', '9642907288', 'roma456')

    def test_define_calling_tickets(self):
        self.assertTrue(self.ND.define_call_ts('Позвонить клиенту 15.09.2019 00:00'))

    def test_definde_satellit_ticket(self):
        self.assertTrue(self.ND.definde_satellit_ticket('Закрыта 15.09.2019 00:00'))