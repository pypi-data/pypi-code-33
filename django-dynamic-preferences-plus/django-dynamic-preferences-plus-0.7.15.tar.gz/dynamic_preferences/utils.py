# !/usr/bin/env python
# encoding:UTF-8

import collections
import os
from django.conf import settings
from dynamic_preferences.settings import preferences_settings


def update(d, u):
    """
        Custom recursive update of dictionary
        from http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def get_default_file_path(filename):
    return os.path.join(settings.PROJECT_DIR, preferences_settings.FILE_PREFERENCE_REL_DEFAULT_DIR, filename)


def get_upload_file_path(filename):
    return os.path.join(settings.MEDIA_ROOT, preferences_settings.FILE_PREFERENCE_REL_UPLOAD_DIR, filename)

# def get_static_dynamic_prefereces_dir():
#     from distutils.sysconfig import get_python_lib
#     return get_python_lib() + 'django-dynamic-preferences/django_preferences/media',
