from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag()
def karvi_settings(value):
    if value == "sitename":
        return settings.KARVI_SITENAME
    if value == "homepage":
        return settings.KARVI_HOMEPAGE
    if value == "version":
        return settings.KARVI_VERSION
    pass
