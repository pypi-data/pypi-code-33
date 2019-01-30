# !/usr/bin/env python
# encoding:UTF-8

# Taken from django-rest-framework
# https://github.com/tomchristie/django-rest-framework
# Copyright (c) 2011-2015, Tom Christie All rights reserved.
from django.core.exceptions import ImproperlyConfigured

SETTINGS_ATTR = 'DYNAMIC_PREFERENCES'
USER_SETTINGS = None

try:
    from django.conf import settings
except ImportError:
    pass
else:
    # Only pull Django settings if Django environment variable exists.
    if settings.configured:
        USER_SETTINGS = getattr(settings, SETTINGS_ATTR, None)
    if not settings.MEDIA_URL:
        raise ImproperlyConfigured('Requested setting MEDIA_URL, but settings are not configured. You must either '
                                   'define the environment variable MEDIA_URL before continuing.')
    if not settings.PROJECT_DIR:
        raise ImproperlyConfigured('Requested setting PROJECT_DIR, but settings are not configured. You must either '
                                   'define the environment variable PROJECT_DIR before continuing.\n'
                                   'PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))')


DEFAULTS = {
    'FILE_PREFERENCE_REL_UPLOAD_DIR': 'dynamic_preferences',    # from MEDIA_ROOT
    'FILE_PREFERENCE_REL_DEFAULT_DIR': 'default'                # from PROJECT_DIR
}


class PreferenceSettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from rest_framework.settings import api_settings
        print(api_settings.DEFAULT_RENDERER_CLASSES)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid preference setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val


preferences_settings = PreferenceSettings(USER_SETTINGS, DEFAULTS)
