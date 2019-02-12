from contextlib import ContextDecorator
from importlib import import_module

from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed


# TODO add checking for required settings
DEFAULTS = {
    "ENV": None,
    "SERVICE": None,
    "QUEUES": [],
    "CONSUMER_CLASS": "mbq.pubsub.consumer.Consumer",
    "MESSAGE_HANDLERS": {},
    "DEFAULT_HANDLER": None,
    "USE_DATABASE": True,
}

IMPORT_STRINGS = {"CONSUMER_CLASS", "MESSAGE_HANDLERS", "DEFAULT_HANDLER"}


# The following is heavily inspired by the approach used in
# Django Restframework: https://github.com/encode
# /django-rest-framework/blob/master/rest_framework/settings.py
#
# Copyright © 2011-present, Encode OSS Ltd. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif isinstance(val, dict):
        return {k: import_from_string(v, setting_name) for k, v in val.items()}
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        module_path, class_name = val.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not import '{val}' for PubSub setting '{setting_name}'. {e.__class__.__name__}: {e}."
        )


class ProjectSettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "PUBSUB", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid PUBSUB setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")

    def __call__(self, **overrides):
        """
        ContextDecorator for use in testing.
        """

        settings = self
        originals = {}
        UNSET = object()

        class contextdecorator(ContextDecorator):
            def __enter__(self):
                for k, v in overrides.items():
                    if hasattr(settings, k):
                        originals[k] = getattr(settings, k)
                    else:
                        originals[k] = UNSET
                    setattr(settings, k, v)

            def __exit__(self, *exc):
                for k, v in originals.items():
                    if v is UNSET:
                        delattr(settings, k)
                    else:
                        setattr(settings, k, v)

        return contextdecorator()


project_settings = ProjectSettings(None, DEFAULTS, IMPORT_STRINGS)


@receiver(setting_changed)
def reload_api_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "PUBSUB":
        project_settings.reload()
