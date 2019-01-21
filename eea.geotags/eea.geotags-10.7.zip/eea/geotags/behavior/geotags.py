from zope.interface import provider
from zope.interface import implementer

from zope import schema

from Acquisition import ImplicitAcquisitionWrapper
from Acquisition import aq_self

from plone.supermodel import model
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider

from eea.geotags.behavior.widget import GeotagFieldWidget
from eea.geotags.config import _

from eea.geotags.field.common import json2list
from eea.geotags.field.common import set_json
from eea.geotags.field.common import get_tags


@provider(IFormFieldProvider)
class ISingleGeoTag(model.Schema):

    model.fieldset(
        'geo_coverage',
        label=_(u'Geo coverage'),
        fields=('location', )
    )

    location = schema.Text(title=_(u'Location'), required=False)
    directives.widget('location', GeotagFieldWidget, multiline=0)


@provider(IFormFieldProvider)
class IMultiGeoTag(model.Schema):

    model.fieldset(
        'geo_coverage',
        label=_(u'Geo coverage'),
        fields=('location', )
    )

    location = schema.Text(title=_(u'Location'), required=False)
    directives.widget('location', GeotagFieldWidget, multiline=1)


@implementer(ISingleGeoTag, IMultiGeoTag)
class GeoTag(object):

    def __init__(self, context):
        # De-wrap context when a Dexterity object is added
        # (taken from collective.geo.behaviour).
        if isinstance(context, ImplicitAcquisitionWrapper):
            context = aq_self(context)
        self.context = context

    @property
    def location(self):
        value = json2list(get_tags(self.context))
        return '\n'.join(value) if value is not None else value

    @location.setter
    def location(self, value):
        set_json(self.context, value)
