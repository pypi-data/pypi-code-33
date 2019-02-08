import os
import importlib
from distutils.util import strtobool
from t3.env import load_env
from t3.django.util import get_base_dir


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = get_base_dir()


# Get env dictionary.  This feeds from env, .env, and then vcap services
# For local dev, move .env.example to .env and play with settings
# In CI, a service.yaml is likely to be used
_env = load_env(dot_env_path=BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.getenv('DJANGO_DEBUG', 'false')))

# Store this as a comma delimited list (eg. localhost,127.0.0.1)
ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')


# Create of merge INSTALLED_APPS
# INSTALLED_APPS = globals().get('INSTALLED_APPS', [])
CORE_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party Packages
    'django_prometheus',
    'storages',
    'django_extensions',
    'corsheaders',
]


# Django Middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',

    # 3rd Party Middleware
    'log_request_id.middleware.RequestIDMiddleware',
]

# Django Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': int(os.getenv('DB_PORT')) if os.getenv('DB_PORT') else None,
        'TEST': {
            'ENGINE': os.getenv('DB_TEST_ENGINE', 'django.db.backends.sqlite3'),
            'NAME': os.getenv('DB_TEST_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
            'USER': os.getenv('DB_TEST_USER'),
            'PASSWORD': os.getenv('DB_TEST_PASSWORD'),
            'HOST': os.getenv('DB_TEST_HOST'),
            'PORT': int(os.getenv('DB_TEST_PORT')) if os.getenv('DB_TEST_PORT') else None,
        }
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
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

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ############################################################################
# T3 Specific Configs
# ############################################################################
try:
    PROJECT_PACKAGE = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]
except KeyError:
    PROJECT_PACKAGE = None

LOGGING_LEVEL = os.getenv('DJANGO_LOGGING_LEVEL', 'INFO')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        }
    },
    'formatters': {
        'simple': {
            'format': u'%(asctime)s [%(levelname)-8s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': u'%(asctime)s [%(levelname)-8s] %(message)s',
        },
        'json': {
            '()': 't3.django.log.DjangoJsonFormatter',
        },
        'json_pretty': {
            '()': 't3.django.log.DjangoJsonPrettyFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_pretty',
            'stream': 'ext://sys.stdout',
            'filters': ['request_id'],
        },
    },
    'loggers': {
        't3': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'django': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

if PROJECT_PACKAGE:
    LOGGING['loggers'][PROJECT_PACKAGE] = LOGGING['loggers']['t3']

# Log header stuff
# https://github.com/dabapps/django-log-request-id
LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = "RESPONSE_HEADER_NAME"
REQUEST_ID_RESPONSE_HEADER = "X-Response-Id"


# URL Prefix Stuff
URL_PREFIX = os.getenv('URL_PREFIX', '')
if URL_PREFIX != '':
    # Make sure URL_PREFIX ends with a '/'
    if not URL_PREFIX.endswith('/'):
        URL_PREFIX = URL_PREFIX + '/'
    # Make sure URL_PREFIX doesn't start with '/'
    if URL_PREFIX.startswith('/'):
        URL_PREFIX = URL_PREFIX[1:]


# ############################################################################
# AWS Configs
# ############################################################################
AWS_STORAGE = bool(strtobool(os.getenv('AWS_STORAGE', 'false')))
AWS_LOGGING = bool(strtobool(os.getenv('AWS_LOGGING', 'false')))

# Shared AWS Configs
if AWS_STORAGE or AWS_LOGGING:
    AWS_SERVICE_NAME = os.environ['AWS_SERVICE_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_REGION_NAME = os.environ['AWS_REGION_NAME']

# AWS S3 Storage
if AWS_STORAGE:
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_AUTO_CREATE_BUCKET = True
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', AWS_REGION_NAME)

    AWS_S3_OBJECT_PARAMETERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'CacheControl': 'max-age=94608000',
    }

    # Default media bucket
    DEFAULT_FILE_STORAGE = 't3.django.storages.MediaStorage'
    MEDIAFILES_BUCKET = os.getenv('AWS_MEDIAFILES_BUCKET', AWS_STORAGE_BUCKET_NAME)
    MEDIAFILES_LOCATION = os.getenv('AWS_MEDIAFILES_LOCATION', AWS_SERVICE_NAME + '/' + 'media')

    # Default static bucket
    STATICFILES_STORAGE = 't3.django.storages.StaticStorage'
    STATICFILES_BUCKET = os.getenv('AWS_STATICFILES_BUCKET', AWS_STORAGE_BUCKET_NAME)
    STATICFILES_LOCATION = os.getenv('AWS_STATICFILES_LOCATION', AWS_SERVICE_NAME + '/' + 'static')
else:
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = os.getenv('STATIC_URL', f'/{URL_PREFIX}static/')


# AWS CloudWatch Logging
if AWS_LOGGING:
    Session = importlib.import_module('boto3.session').Session

    # Add handler for CloudWatch (watchtower)
    AWS_DEFAULT_REGION = AWS_REGION_NAME
    LOGGING['handlers']['watchtower'] = {
        'formatter': 'json',
        'class': 'watchtower.django.DjangoCloudWatchLogHandler',
        'log_group': 'django',
        'stream_name': AWS_SERVICE_NAME,
        'filters': ['request_id'],
    }

    # Log using watchtower handler
    LOGGING['loggers']['t3']['handlers'] = ['console', 'watchtower']
    LOGGING['loggers']['django']['handlers'] = ['console', 'watchtower']

    if PROJECT_PACKAGE:
        LOGGING['loggers'][PROJECT_PACKAGE] = LOGGING['loggers']['t3']

# Django Extensions
SHELL_PLUS = "ipython"
IPYTHON_KERNEL_DISPLAY_NAME = "Django Shell-Plus"


# ############################################################################
# CORS Configs
# ############################################################################
# https://github.com/ottoyiu/django-cors-headers
# To see this in the header, then the request header must have `Origin` set
CORS = os.getenv('DJANGO_CORS', '*')
if CORS == '*':
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = ','.split(CORS)

# ############################################################################
# Proxy Configs
# ############################################################################
if bool(strtobool(os.getenv('DJANGO_SECURE_PROXY', 'false'))):
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ############################################################################
# Cache Configs (for calling external GET requests)
# Example:
#   REDIS_CACHE_REGEX: '((restaurants)|(products)).+((menu)|(modifiers))'
#   REDIS_CACHE_TTL: '4'
# Above parameters matches the url paths below with 4 minutes cache life:
#       * restaurants/23kasfe/menu
#       * products/234kasdf/modifiers
# Link: https://cachecontrol.readthedocs.io/en/latest/
# Link: https://regexr.com/ Regular Expression playground
# ############################################################################
REDIS_CACHE = bool(strtobool(os.getenv('REDIS_CACHE', 'false')))
if REDIS_CACHE:
    host = os.environ['REDIS_CACHE_HOST']
    port = os.getenv('REDIS_CACHE_PORT', '6379')
    database = os.getenv('REDIS_CACHE_DB', '0')
    password = os.getenv('REDIS_CACHE_PASS', '')
    passwordStr = f'?password={password}' if password else ''
    EXTERNAL_CACHE = {
        'redis': f'redis://{host}:{port}/{database}{passwordStr}',
        'pattern': os.environ['REDIS_CACHE_REGEX'],
        'minutes': os.environ['REDIS_CACHE_TTL'],
    }


# ############################################################################
# Retry Configs (for calling external REST API requests)
# Example:
#   EXTERNAL_RETRY_NUMBER: 3
#   EXTERNAL_RETRY_FACTOR: 0.3
#   EXTERNAL_RETRY_STATUS_CODES: 500, 502, 503, 504 - Comma separated list
# Above parameters retries the urls externally called for status codes
#   of 500, 502, 503, 504 which is basically server codes, if server is down
#   The above setup retries 3 times with a factor of 0.3.
#   First retry would be 0 seconds later,
#   Second retry would be 0.6 seconds later
#   Third retry would be 1.2 seconds later
# ############################################################################
EXTERNAL_RETRY = bool(strtobool(os.getenv('EXTERNAL_RETRY', 'false')))
if EXTERNAL_RETRY:
    EXTERNAL_RETRY = {
        'number': os.getenv('EXTERNAL_RETRY_NUMBER', '2'),
        'factor': os.getenv('EXTERNAL_RETRY_FACTOR', '0.1'),
        'status_codes': os.getenv('EXTERNAL_RETRY_STATUS_CODES', '500, 502'),
    }
