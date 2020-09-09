from __future__ import absolute_import
from .celery import app as celery_app
from gevent import monkey as curious_george

curious_george.patch_all(thread=False, select=False)
