import os
import sys

DEBUG = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_TO_BD_DIR = BASE_DIR
while not SAVE_TO_BD_DIR.endswith('save_to_db'):
    SAVE_TO_BD_DIR = os.path.dirname(SAVE_TO_BD_DIR)
SAVE_TO_BD_DIR = os.path.dirname(SAVE_TO_BD_DIR)
sys.path.insert(0, SAVE_TO_BD_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        #'NAME': os.path.join(BASE_DIR, 'db_django.sqlite3'),
    }
}

INSTALLED_APPS = ('orm_only',)

SECRET_KEY = 'SECRET_KEY'
