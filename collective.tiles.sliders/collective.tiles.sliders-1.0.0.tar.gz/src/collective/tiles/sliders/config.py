# -*- coding: utf-8 -*-
"""Configuration options for collective.tiles.sliders."""
import pkg_resources


try:
    pkg_resources.get_distribution('plone.app.mosaic')
except pkg_resources.DistributionNotFound:
    HAS_MOSAIC = False
else:
    HAS_MOSAIC = True

PROJECT_NAME = 'collective.tiles.sliders'
PROFILE_ID = u'{0}'.format(PROJECT_NAME)
BASE_PROFILE = '{0}:base'.format(PROFILE_ID)
INSTALL_PROFILE = '{0}:default'.format(PROFILE_ID)
UNINSTALL_PROFILE = '{0}:uninstall'.format(PROFILE_ID)
NON_INSTALLABLE_PROFILES = [UNINSTALL_PROFILE, BASE_PROFILE]
