"""Base settings for a Django Rest Framework Project."""
import os
from distutils.util import strtobool
from t3.env import load_env
from t3.django.util import get_base_dir


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = get_base_dir()


# Get env dictionary.  This feeds from env, .env, and then vcap services
# For local dev, move .env.example to .env and play with settings
# In CI, a service.yaml is likely to be used
_env = load_env(dot_env_path=BASE_DIR)


# Create of merge INSTALLED_APPS
# print(globals().get('INSTALLED_APPS', []))
# INSTALLED_APPS = globals().get('INSTALLED_APPS', [])
# print(globals().get('INSTALLED_APPS', []))
DRF_INSTALLED_APPS = [
    'django_filters',
    'crispy_forms',
    'rest_framework',
    'drf_yasg',
    'rest_framework.authentication'
]


# Rest Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'EXCEPTION_HANDLER': 't3.drf.views.enveloped_exception_handler',
    'PAGE_SIZE': 25,
}

DOCS_TITLE = os.getenv('DOCS_TITLE', 'T3 API')
DOCS_VERSION = os.getenv('DOCS_VERSION', 'v1')

# Set up Swagger to Accept Authorization tokens for particular requests.
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# ############################################################################
# Enables auth configurations for Punchh.  The Punchh Adapter returns JWTs that
# includes tokens that are necessary for both the `v1` api, as well as the `v2`
# api.
# To use, use the `t3.vendors.punchh.PunchhAuthentication` class
# See https://www.django-rest-framework.org/api-guide/authentication/ for more
# ############################################################################
# details on how auth w/ DRF works.
PUNCHH_AUTH = bool(strtobool(os.getenv('PUNCHH_AUTH', 'false')))
if PUNCHH_AUTH:
    # We're using the Punchh Client Secret to sign our JWTs.  It's supposed to
    # be secret and we want all JWTs to become invalid if we need to change it.
    PUNCHH_CLIENT_SECRET = os.environ['PUNCHH_CLIENT_SECRET']

    # Enable PUNCHH_AUTH_SERVER_VERIFY if you want to ping punchh's server with
    # a request, to ensure that the tokens in the JWT are valid.  This is
    # important when adding Punchh auth to services that are not either hitting
    # Punchh's servers directly, or are leveraging Punchh's SSO.
    PUNCHH_AUTH_SERVER_VERIFY = bool(strtobool(os.getenv('PUNCHH_AUTH_SERVER_VERIFY', 'false')))
    # PUNCHH_AUTH_SERVER_VERIFY = True if str(os.getenv('PUNCHH_AUTH_SERVER_VERIFY', 'false')).lower() == 'true' else False
    if PUNCHH_AUTH_SERVER_VERIFY:
        PUNCHH_BASE_URL = os.environ['PUNCHH_BASE_URL']
        PUNCHH_V2_BASE_URL = os.environ['PUNCHH_V2_BASE_URL']
        PUNCHH_CLIENT_KEY = os.environ['PUNCHH_CLIENT_KEY']
