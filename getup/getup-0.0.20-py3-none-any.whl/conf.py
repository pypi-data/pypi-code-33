import functools
import collections.abc as collections
from typing import List, Dict, Tuple, Optional, Union, Any, Iterable
from pydantic import BaseModel, DSN, BaseSettings, PyObject, UrlStr, NameEmail
import dj_database_url

DEFAULT_APPS = [
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

DEFAULT_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

DEFAULT_TEMPLATES = [
    {
        "APP_DIRS": True,
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


class TemplateOptionsConfig(BaseModel):
    context_processors: List[str] = [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]


class TemplateConfig(BaseModel):
    APP_DIRS: bool = True
    BACKEND: str = "django.template.backends.django.DjangoTemplates"
    DIRS: List[str] = []
    OPTIONS: TemplateOptionsConfig


class DatabaseConfig(BaseModel):
    ENGINE: str = "django.db.backends.postgresql"
    NAME: str
    USER: Optional[str]
    PASSWORD: Optional[str]
    HOST: Optional[str]
    PORT: Optional[int]


class DsnConfig(BaseModel):
    dsn: DSN = None


class Configuration(BaseSettings):
    DEBUG: bool = True
    ROOT_URLCONF: Optional[List[Any]] = []
    INSTALLED_APPS: List[str] = DEFAULT_APPS
    MIDDLEWARE: List[str] = DEFAULT_MIDDLEWARE
    SECRET_KEY: str = "hoh"
    STATIC_URL: str = "/static/"
    TEMPLATES: List[TemplateConfig] = DEFAULT_TEMPLATES
    ALLOWED_HOSTS: List[str] = ["localhost"]
    DATABASES: Optional[Dict[str, DatabaseConfig]] = {}
    dsn: Optional[DSN] = None
    extras: Optional[Dict[str, Any]]
    getup_urls: Optional[Any]

    
    def dsn_to_db_conf(self):
        if self.dsn:
            self.DATABASES = {"default": dj_database_url.parse(self.dsn)}
    

    def configure(self):
        """
        Configure Django per configuration
        """
        self.dsn_to_db_conf()
        conf = self.dict()
        if self.extras:
            conf.update(**{k:v for k,v in self.extras.items() if not k in conf})
        sentry_config(conf)
        manual_setup(conf)


class AnymailOptionsConfig(BaseModel):
    MAILGUN_API_KEY: str
    MAIL_MAILGUN_API: UrlStr
    MAIL_MAILGUN_DOMAIN: str


class AnymailConfig(BaseSettings):
    ANYMAIL: AnymailOptionsConfig
    DEFAULT_FROM_EMAIL: NameEmail
    EMAIL_BACKEND: str = 'anymail.backends.mailgun.EmailBackend'


class SentryConfig(BaseModel):
    dsn: str
    release: Optional[str]


def sentry_config(conf:dict, app_dir:str = None) -> dict:
    """
    Configure Sentry/Raven into configuration dict
    
    TODO: Use inheritance
    """
    if conf.get('SENTRY_DSN'):
        import raven

        if app_dir:
            SentryConfig(dsn=conf.SENTRY_DSN, release=raven.fetch_git_sha(app_dir))
        else:
            SentryConfig(dsn=conf.SENTRY_DSN)
        
        conf["INSTALLED_APPS"] += ["raven.contrib.django.raven_compat"]
        conf.update(dict(RAVEN_CONFIG=SentryConfig.dict()))


def manual_setup(conf:dict):
    """
    If configuration is meant to happen from scripts &c
    conf is supposed to be dictionary to override defaults
    """
    from django.conf import settings
    
    if conf.get('ROOT_URLCONF') and not isinstance(conf.get('ROOT_URLCONF'), tuple):
        conf['ROOT_URLCONF'] = tuple(conf.get('ROOT_URLCONF'))

    settings.configure(
        **conf
    )
    import django

    django.setup()
