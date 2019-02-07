import os

from django.template.backends.django import DjangoTemplates
from django.forms.renderers import BaseRenderer, ROOT
from django.conf import settings
from django.utils.functional import cached_property


DEFAULT_SETTINGS = {
    'APP_DIRS': True,
    'DIRS': [],
    'NAME': 'djangoforms',
    'OPTIONS': {},
}


class SdhFormRenderer(BaseRenderer):
    backend = DjangoTemplates

    def get_template(self, template_name):
        return self.engine.get_template(template_name)

    @cached_property
    def engine(self):
        try:
            _settings = settings.SDH_RENDERER.copy()
        except AttributeError:
            _settings = DEFAULT_SETTINGS.copy()

        _settings['DIRS'].append(os.path.join(ROOT, DjangoTemplates.app_dirname))
        return self.backend(_settings)
