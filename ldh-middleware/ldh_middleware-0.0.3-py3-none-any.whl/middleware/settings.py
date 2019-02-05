import ldap
import strictyaml
from decouple import Config, Csv, RepositoryIni
from django_auth_ldap.config import LDAPSearch

import purist.limitmonitor
from .settings_original import *

#
# LOAD CONFIGURATION FILE
#

CONFIG_PATH = '/etc/opt/purist/middleware/config.ini'
SECRET_PATH = '/etc/opt/purist/middleware/secret.ini'
LINK_PROFILE_PATH = '/etc/opt/purist/middleware/link_profile.strict.yml'

config = Config(RepositoryIni(CONFIG_PATH))
secret_config = Config(RepositoryIni(SECRET_PATH))

with open(LINK_PROFILE_PATH, 'r') as stream:
    LINK_PROFILE_ORDERED_DICT = strictyaml.load(stream.read()).data

#
# SECURITY
#

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

# it is safe to use these flags in production
DEBUG_ALL_ACCESS = config("DEBUG_ALL_ACCESS", cast=bool)
DEBUG_CHANGE_PASSWORD = config("DEBUG_CHANGE_PASSWORD", cast=bool)
DEBUG_SKIP_ACTIVATION_COMMAND = config("DEBUG_SKIP_ACTIVATION_COMMAND", cast=bool)
DEBUG_SKIP_VALIDATE_ON_AUTHENTICATION = config("DEBUG_SKIP_VALIDATE_ON_AUTHENTICATION", cast=bool)

# Required if DEBUG is False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

#
# INSTALLED APPLICATIONS
#

INSTALLED_APPS += ["crispy_forms", "django_agpl", "django_celery_beat", "django_extensions", "ldapregister",
                   "limitmonitor", "purist"]

#
# AGPL APPLICATION
#

AGPL_ROOT = os.path.abspath(os.path.dirname(__file__) + "/..")

# no special exclusions are required, configuration and secrets are not stored in the site folder
AGPL_EXCLUDE_DIRS = [
    r'\.git$',
    r'\.idea$',
]

AGPL_FILENAME_PREFIX = 'middleware'

#
# REGISTRATION APPLICATION
#

REGISTRATION_OPEN = config("REGISTRATION_OPEN", cast=bool)

REG_PERSON_BASE_DN = config("REG_PERSON_BASE_DN")
REG_PERSON_OBJECT_CLASSES = config("REG_PERSON_OBJECT_CLASSES", cast=Csv())

REG_GROUP_BASE_DN = config("REG_GROUP_BASE_DN")
REG_GROUP_OBJECT_CLASSES = config("REG_GROUP_OBJECT_CLASSES", cast=Csv())

#
#  AUTHENTICATION
#

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'purist.custom.PassphraseValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'purist.custom.AuthenticationBackend',
)

AUTH_LDAP_SERVER_URI = config("AUTH_LDAP_SERVER_URI")
AUTH_LDAP_START_TLS = config("AUTH_LDAP_START_TLS", cast=bool)

AUTH_LDAP_BIND_DN = config("AUTH_LDAP_BIND_DN")
AUTH_LDAP_BIND_PASSWORD = secret_config("AUTH_LDAP_BIND_PASSWORD")

BASE_DN = config("AUTH_LDAP_USER_SEARCH_BASE_DN")
AUTH_LDAP_USER_SEARCH = LDAPSearch(BASE_DN, ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# must match `base_dn` and primary key in `ldapregister.models.LdapPerson`

AUTH_USER_MODEL = 'purist.User'

#
# DATABASE
#

# See also:
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# and https://pypi.python.org/pypi/django-ldapdb/
# (re-uses LDAP connection details from authentication settings)

SQLITE_DB_PATH = config("SQLITE_DB_PATH")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SQLITE_DB_PATH,
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': AUTH_LDAP_SERVER_URI,
        'USER': AUTH_LDAP_BIND_DN,
        'PASSWORD': AUTH_LDAP_BIND_PASSWORD,
        'TLS': AUTH_LDAP_START_TLS,
    },
}

DATABASE_ROUTERS = ['ldapdb.router.Router']

#
# STATIC AND SITE SETTINGS
#

STATIC_ROOT = config("STATIC_ROOT")
STATICFILES_DIRS = config("STATICFILES_DIRS", cast=Csv())
SITE_TITLE = config("SITE_TITLE")
SITE_BYLINE = config("SITE_BYLINE")
SITE_DOMAIN = config("SITE_DOMAIN")
SITE_PROVIDER = config("SITE_PROVIDER")
SITE_PROVIDER_LINK = config("SITE_PROVIDER_LINK")

#
# WOOCOMMERCE
#

WOO_URL = config("WOO_URL")
WOO_WP_API = config("WOO_WP_API", cast=bool)
WOO_VERSION = config("WOO_VERSION")
WOO_QUERY_STRING_AUTH = config("WOO_QUERY_STRING_AUTH", cast=bool)  # required for OAuth over HTTPS

WOO_CONSUMER_KEY = secret_config("WOO_CONSUMER_KEY")
WOO_CONSUMER_SECRET = secret_config("WOO_CONSUMER_SECRET")

#
# WOOSUB1 PARSER
#

WOOSUB1_PRODUCT_LIST = config("WOOSUB1_PRODUCT_LIST", cast=Csv(int))

#
# SSH CONNECTION TO OPENVPN SERVER
#

OVPN_HOSTNAME = config("OVPN_HOSTNAME")
OVPN_PORT = config("OVPN_PORT", cast=int)
OVPN_USERNAME = config("OVPN_USERNAME")
OVPN_FILEPATH = config("OVPN_FILEPATH")

#
# LIMIT MONITOR
#

LM_SERVICES = purist.limitmonitor.ServicesContainer
LM_PARSERS = purist.limitmonitor.ParserContainer

#
# LOGGING
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
