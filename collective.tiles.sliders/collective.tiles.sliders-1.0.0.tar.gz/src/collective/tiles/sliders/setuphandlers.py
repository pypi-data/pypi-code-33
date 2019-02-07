# -*- coding: utf-8 -*-
"""Post install import steps for collective.tiles.sliders."""
from collective.tiles.sliders.config import NON_INSTALLABLE_PROFILES
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Define hidden GS profiles."""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return NON_INSTALLABLE_PROFILES
