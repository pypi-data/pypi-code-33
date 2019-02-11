import os

import boto3
import dj_database_url
from mbq import env, metrics


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ["pubsub.lcl.mbq.io"]

DEBUG = True

DEBUG_PROPAGATE_EXCEPTIONS = True

DATABASE_URL = env.get("DATABASE_URL", required=False)

if DATABASE_URL is not None:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL, engine="django.db.backends.postgresql", conn_max_age=0
        )
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

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
    "mbq.pubsub",
    "tests",
]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

USE_TZ = True

MESSAGE_HANDLERS = "tests.message_handlers"

PUBSUB = {
    "ENV": env.Environment.LOCAL,
    "SERVICE": "pubsub",
    "QUEUES": ["updates"],
    "MESSAGE_HANDLERS": {
        "pubsub.update_raise_exception": f"{MESSAGE_HANDLERS}.handle_update_raise_exception"
    },
    "PAPERTRAIL_URL": "https://papertrailapp.com/systems/convox-prd-invoicing-prd-LogGroup-13EROOLI94RC4",
}

LOGGING_LEVEL = "DEBUG"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(levelname)-8s %(asctime)s %(name)s " "%(filename)s:%(lineno)s %(message)s"
            )
        }
    },
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "verbose"}
    },
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": LOGGING_LEVEL, "propagate": False},
        "botocore": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "boto3": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "": {"handlers": ["console"], "level": LOGGING_LEVEL},
    },
}

AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID", required=False)
AWS_DEFAULT_REGION = env.get("AWS_DEFAULT_REGION", required=False)
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY", required=False)

if AWS_ACCESS_KEY_ID is not None:
    boto3.setup_default_session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )

metrics.init("pubsubtest", env=env.Environment.LOCAL)
