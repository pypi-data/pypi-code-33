import attr
import functools
import collections.abc as collections

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


@attr.s(auto_attribs=True)
class Configuration:
    DEBUG: bool = True
    ROOT_URLCONF: tuple = tuple()
    INSTALLED_APPS: list = DEFAULT_APPS
    MIDDLEWARE: list = DEFAULT_MIDDLEWARE
    SECRET_KEY: str = "hoh"
    STATIC_URL: str = "/static/"
    TEMPLATES: list = DEFAULT_TEMPLATES
    ALLOWED_HOSTS: list = ["localhost"]
    DATABASES: dict = {}

    def replace(self, **kwargs):
        {setattr(self, k, v) for k, v in kwargs.items()}

    def combine(self, *args):
        """
        Given one or more Configuration objects add them together
        Iterables are concatenated, other type of values replaced
        Right most argument wins
        """

        def adder(out, obj):

            for afield in attr.fields(self.__class__):
                field = afield.name
                value = getattr(obj, field)
                if isinstance(value, list):
                    setattr(out, field, value + getattr(out, field))
                elif isinstance(value, dict):
                    getattr(out, field).update(value)
                else:
                    setattr(out, field, value)

            return out

        functools.reduce(adder, args, self)


def env_setup(conf, app_dir=False):
    import os
    import environ
    # Convenience for some environment settings
    env = environ.Env(
        DEBUG=(bool, conf.DEBUG),
        SECRET_KEY=(str, conf.SECRET_KEY),
        ALLOWED_HOSTS=(list, []),
        DATABASE_URL=(str, ""),
        SENTRY_DSN=(str, ""),
    )
    environ.Env.read_env()
    conf.replace(
        DEBUG=env("DEBUG"),
        ALLOWED_HOSTS=env("ALLOWED_HOSTS"),
        # Well you need to keep some secrets,
        SECRET_KEY=env("SECRET_KEY"),
    )
    if os.environ.get("DATABASE_URL"):
        conf.replace(DATABASES={"default": env.db()})

    # Wish this was simpler
    if env("SENTRY_DSN"):
        import raven

        raven_config = {"dsn": env("SENTRY_DSN")}
        if app_dir:
            raven_config["release"] = raven.fetch_git_sha(app_dir)

        conf.combine(
            Configuration(
                INSTALLED_APPS=["raven.contrib.django.raven_compat"],
                RAVEN_CONFIG=raven_config,
            )
        )
