from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from urllib.parse import unquote


class Command(BaseCommand):
    help = 'Decode all active sessions'

    def handle(self, *args, **options):
        sessions = Session.objects.all()
        for session in sessions:
            uid = unquote(str(session.get_decoded()))
            self.stdout.write(self.style.SUCCESS(uid))