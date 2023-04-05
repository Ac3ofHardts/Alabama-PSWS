import os
from .base import *

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = ['pswsnetwork.caps.ua.edu', 'www.pswsnetwork.caps.ua.edu', '130.160.26.22','psws.hamsci.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'AndersonTestingDB',
        'USER': 'abliddle',
        'PASSWORD': os.environ["PROD_DB_PASS"],
  #       'CONN_MAX_AGE': None,  # WDE - persistent connections
        'HOST': 'localhost',
        'PORT': '',
        }
}

