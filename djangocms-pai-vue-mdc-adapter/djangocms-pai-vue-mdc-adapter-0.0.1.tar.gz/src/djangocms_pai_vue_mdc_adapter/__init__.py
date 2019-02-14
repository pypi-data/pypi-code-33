# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'djangocms-pai-vue-mdc-adapter'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

default_app_config = 'djangocms_pai_vue_mdc_adapter.apps.DjangocmsPaiVueMdcAdapterConfig'
