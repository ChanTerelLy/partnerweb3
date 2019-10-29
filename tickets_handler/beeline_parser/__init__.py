from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
# __import__('gevent.monkey').monkey.patch_all()
# from requests.packages.urllib3.util.ssl_ import create_urllib3_context
