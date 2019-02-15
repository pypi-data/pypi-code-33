from mbq import env, metrics


SECRET_KEY = "fake-key"
DEBUG = True
RANCH = {"env": "Test", "service": "test-service"}
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
INSTALLED_APPS = ["mbq.ranch"]
USE_TZ = True
metrics.init("ranch-test", env.Environment.LOCAL)
