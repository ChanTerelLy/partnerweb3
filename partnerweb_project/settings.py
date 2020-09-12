import os
import django_heroku
from django.utils import timezone
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = int(os.getenv('DEBUG'))
DEBUG_PROPAGATE_EXCEPTIONS = True
ALLOWED_HOSTS = ['*']
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('SENDER_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMINS = [('Admin', os.getenv('ADMIN_EMAIL'))]

LOGOUT_REDIRECT_URL = 'logout'
LOGIN_REDIRECT_URL = 'login'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
LOGIN_URL = 'login'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'territory.apps.TerritoryConfig',
    'analytic.apps.AnalyticConfig',
    'debug_toolbar',
    'tickets_handler',
	'widget_tweaks',
    'crispy_forms',
    'call_center',
    'storages',
    'bootstrap_pagination',
    'rest_framework',
    "fcm_django"
]
FCM_DJANGO_SETTINGS = {
        "FCM_SERVER_KEY": os.getenv('FCM_SERVER_KEY'),
         # true if you want to have only one active device per registered user at a time
         # default: False
        "ONE_DEVICE_PER_USER": False,
         # devices to which notifications cannot be sent,
         # are deleted upon receiving error response from FCM
         # default: False
        "DELETE_INACTIVE_DEVICES": False,
}

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

#TODO:don't send email, maybe gevent problem?
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

ROOT_URLCONF = 'partnerweb_project.urls'

INTERNAL_IPS = [
    '127.0.0.1',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'partnerweb_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
    },
    'second': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SECOND_DB_NAME'),
        'USER': os.getenv('SECOND_DB_USER'),
        'PASSWORD': os.getenv('SECOND_DB_PASSWORD'),
        'HOST': os.getenv('SECOND_DB_HOST'),
        'PORT': '5432',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
USE_REDIS = int(os.getenv('USE_REDIS'))
if USE_REDIS:
    CACHES = {
        "default": {
            'TIMEOUT': None,
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get('REDIS_URL'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

django_heroku.settings(locals())

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap4'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

USE_S3 = int(os.getenv('USE_S3'))
USE_S3_STATIC = int(os.getenv('USE_S3_STATIC'))
if USE_S3:
    AWS_S3_REGION_NAME = 'eu-west-2'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    if USE_S3_STATIC:
        STATIC_LOCATION = f'static-{os.getenv("BRANCH")}'if os.getenv('BRANCH') else 'static'
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
        STATICFILES_STORAGE = 'partnerweb_project.storage_backends.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'partnerweb_project.storage_backends.PublicMediaStorage'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_FILE_STORAGE = 'partnerweb_project.storage_backends.PrivateMediaStorage'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


DJANGORESIZED_DEFAULT_SIZE = [720, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True
YA_METRIC_ID = int(os.getenv('YA_METRIC_ID')) if os.getenv('YA_METRIC_ID') else False


#Celery
ROKER_URL = os.getenv('REDIS_URL')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL')
CELERY_ACCEPT_CONTENT = [os.getenv('CELERY_ACCEPT_CONTENT')]
CELERY_TASK_SERIALIZER = os.getenv('CELERY_TASK_SERIALIZER')
CELERY_RESULT_SERIALIZER = os.getenv('CELERY_RESULT_SERIALIZER')
CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE')
CELERY_REDIS_MAX_CONNECTIONS = 10
