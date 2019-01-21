""" Migrate to registry.
"""

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from eea.geotags.controlpanel.interfaces import IGeotagsSettings


import plone.api as api


def migrate_to_registry(_):
    ptool = api.portal.get_tool('portal_properties')
    gprops = getattr(ptool, 'geographical_properties', None)
    google_key = getattr(gprops, 'google_key', u'')
    geonames_key = getattr(gprops, 'geonames_key', u'')

    settings = getUtility(IRegistry).forInterface(IGeotagsSettings, False)
    settings.maps_api_key = (
        google_key.decode('utf-8') if google_key
        else settings.maps_api_key)

    settings.geonames_key = (
        geonames_key.decode('utf-8') if geonames_key
        else settings.geonames_key)
