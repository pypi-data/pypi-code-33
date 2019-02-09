from datetime import timedelta

SECRET_KEY = '2^mza*qpug3+htv7jxecatc0w&rluw!b#2cf9r*+&3fj8a2i66'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authentication',
    'tests',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-generic-rest.db',
    }
}
AUTH_USER_MODEL = 'tests.User'
USER_SERIALIZER = 'tests.serializers.UserSerializer'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_URL = '/media/'

TOKEN_EXPIRY = timedelta(hours=1)
REFRESH_TOKEN_EXPIRY = timedelta(days=1)
ROOT_URLCONF = 'authentication.urls'
MIN_PW_LENGTH = 4
CHAR_CLASSES = 1
ERROR_KEY = 'Error'
MAX_IMG_SIZE = 100 * 1024
MAX_IMG_WIDTH = 512
MAX_IMG_HEIGHT = 512

HOST = 'localhost:8000'
DEFAULT_FROM_EMAIL = 'Token Auth <noreply@djangotokenauth.test>'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

RESET_TOKEN_EXPIRY = timedelta(days=1)
VAL_TOKEN_EXPIRY = timedelta(days=3)
