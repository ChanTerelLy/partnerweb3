import unittest

from tickets_handler.beeline_parser import manager


class TestAuth(unittest.TestCase):

    def setUp(self):
        auth = manager.Auth('G800-37', '9642907288', 'roma456')





class TestNewDesign(unittest.TestCase):

    def setUp(self):
        self.ND = manager.NewDesign('G800-37', '9642907288', 'roma456')

    def test_define_calling_tickets(self):
        self.assertTrue(self.ND.define_call_ts('Позвонить клиенту 15.09.2019 00:00'))

    def test_definde_satellit_ticket(self):
        self.assertTrue(self.ND.definde_satellit_ticket('Закрыта 15.09.2019 00:00'))