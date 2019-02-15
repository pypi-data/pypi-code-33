import os

import dj_database_url
from mbq import env, metrics


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = ["ranch.lcl.mbq.io"]
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True
DATABASE_URL = "postgres://postgres:postgres@ranch-postgres:5432/ranch"
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL, engine="django.db.backends.postgresql", conn_max_age=0
    )
}
LAUNCHDARKLY_SDK_KEY = env.get("LAUNCHDARKLY_SDK_KEY", required=False)
SITE_ID = 1
SECRET_KEY = "BACON"
USE_I18N = True
USE_L10N = True
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
ROOT_URLCONF = "tests.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": True,
            "context_processors": {
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            },
        },
    }
]
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "mbq.ranch",
    "tests",
]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
USE_TZ = True
MESSAGE_HANDLERS = "tests.message_handlers"
RANCH = {
    "env": env.Environment.LOCAL,  # e.g. production, development
    "service": "ranch",  # e.g. os-core
}
LOGGING_LEVEL = "DEBUG"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(levelname)-8s %(asctime)s %(name)s "
                "%(filename)s:%(lineno)s %(message)s"
            )
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "botocore": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "boto3": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "": {"handlers": ["console"], "level": LOGGING_LEVEL},
    },
}

metrics.init("ranch", env.Environment.LOCAL, {})
