from __future__ import absolute_import
import os
import sys
from celery import Celery
from django.conf import settings
import os

sys.path.append(os.path.abspath('api'))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'partnerweb_project.settings')
app = Celery('partnerweb_project', broker=os.getenv('REDISCLOUD_URL') + '/0') #secon redis server

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))