from django.conf import settings

if settings.APP_NAME == "edc_base":
    from .tests.models import *  # noqa
