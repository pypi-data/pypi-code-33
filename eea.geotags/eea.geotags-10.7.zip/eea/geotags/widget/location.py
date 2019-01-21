""" Widget
"""
from zope.interface import implements

from zope.schema import Field
from zope.schema.interfaces import IField

from Products.Archetypes.atapi import StringWidget

from eea.geotags.field.location import GeotagsFieldMixin
from eea.geotags.field.common import get_json

from eea.geotags.widget.common import get_js_props
from eea.geotags.widget.common import get_base_url
from eea.geotags.widget.common import get_maps_api_key

from eea.geotags.widget.common import URL_DIALOG
from eea.geotags.widget.common import URL_SIDEBAR
from eea.geotags.widget.common import URL_BASKET
from eea.geotags.widget.common import URL_JSON
from eea.geotags.widget.common import URL_SUGGESTIONS
from eea.geotags.widget.common import URL_COUNTRY_MAPPING


class GeotagsWidget(StringWidget):
    """ Geotags
    """
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': "eea.geotags",
        'dialog': URL_DIALOG,
        'sidebar': URL_SIDEBAR,
        'basket': URL_BASKET,
        'json': URL_JSON,
        'suggestions': URL_SUGGESTIONS,
        'country_mapping': URL_COUNTRY_MAPPING,
    })

    def get_geojson(self, name, context, request):
        # type: () -> str
        return (
            self.postback and request.get(name, None)
            or get_json(context)
        )

    def get_params(self, field, name, context, request):
        geojson = self.get_geojson(name, context, request)
        base_url = get_base_url(request)
        return dict(
            id=name,
            name=name,
            base_url=base_url,
            label=self.Label(context),
            geojson=geojson,
            js_props=get_js_props(field.multiline, name, name, base_url, geojson),
            api_key=get_maps_api_key(),
        )


###
# Formlib widget
######

class IGeotagSingleField(IField):
    """ The field interface
    """

class GeotagMixinField(Field, GeotagsFieldMixin):
    """ Geotag Mixin Field
    """

    def set(self, instance, value, **kwargs):
        """ Set
        """
        self.setJSON(instance.context, value, **kwargs)

class GeotagSingleField(GeotagMixinField):
    """ Geotag Single Field
    """
    implements(IGeotagSingleField)

    @property
    def multiline(self):
        """ Multiline
        """
        return False

class IGeotagMultiField(IField):
    """ The field interface
    """

class GeotagMultiField(GeotagMixinField):
    """ Geotag Multi Field
    """
    implements(IGeotagMultiField)

    @property
    def multiline(self):
        """ Multiline
        """
        return True
