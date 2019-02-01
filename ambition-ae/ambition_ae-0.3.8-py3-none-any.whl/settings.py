import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = "ambition_ae"
ETC_DIR = os.path.join(BASE_DIR, "etc")

# for django.contrib.sites
SITE_ID = 40
REVIEWER_SITE_ID = 0
RANDOMIZATION_LIST_PATH = os.path.join(
    BASE_DIR, APP_NAME, "tests", "test_randomization_list.csv"
)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "es5a=8sat3j^mpl0nd28nv+(@#71^%2)-$wty=l@3oknyyr+&t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

LIVE_SYSTEM = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_crypto_fields.apps.AppConfig",
    "django_revision.apps.AppConfig",
    "django_collect_offline.apps.AppConfig",
    "django_collect_offline_files.apps.AppConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "edc_action_item.apps.AppConfig",
    "edc_base.apps.AppConfig",
    "edc_device.apps.AppConfig",
    "edc_identifier.apps.AppConfig",
    "edc_list_data.apps.AppConfig",
    "edc_metadata.apps.AppConfig",
    "edc_notification.apps.AppConfig",
    "edc_prn.apps.AppConfig",
    "edc_protocol.apps.AppConfig",
    "edc_registration.apps.AppConfig",
    "edc_visit_tracking.apps.AppConfig",
    "edc_visit_schedule.apps.AppConfig",
    "ambition_lists.apps.AppConfig",
    "ambition_rando.apps.AppConfig",
    "ambition_prn.apps.AppConfig",
    "ambition_ae.apps.EdcFacilityAppConfig",
    "ambition_ae.apps.AppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "edc_dashboard.middleware.DashboardMiddleware",
    "edc_subject_dashboard.middleware.DashboardMiddleware",
]

ROOT_URLCONF = "ambition_ae.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "ambition_ae.wsgi.application"


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'OPTIONS': {
#             'read_default_file': os.path.join(ETC_DIR, 'mysql.conf'),
#         },
#     },
# }


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Gaborone"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = "/static/"

EMAIL_CONTACTS = {"ae_reports": "user@example.com"}

DASHBOARD_URL_NAMES = {
    "subject_models_url": "subject_models_url",
    "subject_listboard_url": "ambition_dashboard:subject_listboard_url",
    "screening_listboard_url": "ambition_dashboard:screening_listboard_url",
    "subject_dashboard_url": "ambition_dashboard:subject_dashboard_url",
}

DJANGO_COLLECT_OFFLINE_SERVER_IP = None
DJANGO_COLLECT_OFFLINE_FILES_REMOTE_HOST = None
DJANGO_COLLECT_OFFLINE_FILES_USER = None
DJANGO_COLLECT_OFFLINE_FILES_USB_VOLUME = None

COUNTRY = "botswana"
HOLIDAY_FILE = os.path.join(BASE_DIR, APP_NAME, "tests", "holidays.csv")

EDC_BOOTSTRAP = 3

EMAIL_CONTACTS = {
    "data_request": "someone@example.com",
    "data_manager": "someone@example.com",
    "tmg": "someone@example.com",
}
EMAIL_ENABLED = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TWILIO_ENABLED = False

if "test" in sys.argv:

    class DisableMigrations:
        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
    DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"
