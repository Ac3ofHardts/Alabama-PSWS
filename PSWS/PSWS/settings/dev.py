import os
from .base import *

SECRET_KEY = 'eo@tv1y463o4ck6)1ikzk@#a^@p7+so^ah9j__p@1a7slxfyxf'
DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Testing_DB',
        'USER': 'njit',
        'PASSWORD': 'temppass',
  #       'CONN_MAX_AGE': None,  # WDE - persistent connections
        'HOST': 'localhost',
        'PORT': '',
        }
}

