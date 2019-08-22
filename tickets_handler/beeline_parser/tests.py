import unittest
from tickets_handler.beeline_parser import tickets_manager

NewDesing = tickets_manager.NewDesign('G800-37', '9642907288', 'roma456')

class TestTicketsManager(unittest.TestCase):

    def test_define_calling_tickets(self):
        self.assertTrue(NewDesing.define_call_ts('Резерв'))

    def test_definde_satellit_ticket(self):
        self.assertTrue(NewDesing.definde_satellit_ticket('Закрыта'))