""" Interfaces
"""
from zope import schema
from plone.registry import field
from zope.interface import Interface

from eea.geotags.config import _


class IGeotagsSettings(Interface):
    """ Geotags settings
    """

    maps_api_key = schema.TextLine(
        title=_(u"Google Maps API key"),
        description=_(
            u'This will be used to render the Google Maps widget'
            u'for eea.geotags enabled location fields.'
            u'You can get one from https://developers.google.com/maps/documentation/javascript/get-api-key. '
            u'Leave empty to use Open Street Map instead'
        ),
        required=False,
        default=u''
    )

    geonames_key = schema.TextLine(
        title=_(u"Geonames key"),
        description=_(u'http://www.geonames.org/'),
        required=False,
        default=u''
    )


class IGeoVocabularies(Interface):
    geotags = field.Dict(
        title=_(u'Geotags tree'),
        key_type=field.TextLine(),
        value_type=field.Dict(
            key_type=field.TextLine(),
            value_type=field.TextLine(),
        ),
    )

    biotags = field.Dict(
        title=_(u'Biogeographical regions'),
        key_type=field.TextLine(),
        value_type=field.Dict(
            key_type=field.TextLine(),
            value_type=field.TextLine(),
        ),
    )

    countries_mapping = field.Dict(
        title=_(u'EEA Custom Country Name Mappings'),
        key_type=field.TextLine(),
        value_type=field.TextLine(),
    )
