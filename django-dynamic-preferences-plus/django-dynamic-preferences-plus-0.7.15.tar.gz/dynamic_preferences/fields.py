# !/usr/bin/env python
# encoding:UTF-8

import os
import urlparse
from django.conf import settings
from django.utils.encoding import filepath_to_uri

from dynamic_preferences.settings import preferences_settings
from django.db.models.fields.files import FieldFile


class FieldUpfile(FieldFile):

    @staticmethod
    def get_file_url(name):
        return urlparse.urljoin(settings.MEDIA_URL,
                                os.path.join(preferences_settings.FILE_PREFERENCE_REL_UPLOAD_DIR, name))

    @property
    def url(self):
        return self.get_file_url(filepath_to_uri(self.name))
