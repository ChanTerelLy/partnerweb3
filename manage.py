#!/usr/bin/env python
import os
import sys
# TURN ON FOR DEBUG
__import__('gevent.monkey').monkey.patch_all()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'partnerweb_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
