from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only

from zope.schema.interfaces import IField

from z3c.form.browser.textarea import TextAreaWidget

from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget

from z3c.form.widget import FieldWidget

from eea.geotags.widget.common import get_base_url
from eea.geotags.widget.common import get_maps_api_key
from eea.geotags.widget.common import get_js_props
from eea.geotags.field.location import get_json


class IGeotagWidget(IWidget):
    """ """


@implementer_only(IGeotagWidget)
class GeotagWidget(TextAreaWidget):

    klass = u'eea.geolocation.widget'
    multiline = 0

    def get_params(self):
        geojson = self.extract(None) or get_json(self.context)  # type: str
        base_url = get_base_url(self.request)

        w_id = self.id
        w_name = self.name

        js_props = get_js_props(
            self.multiline, w_id, w_name, base_url, geojson)

        return dict(
            id=w_id,
            name=w_name,
            base_url=base_url,
            label=self.label,
            geojson=geojson,
            js_props=js_props,
            api_key=get_maps_api_key(),
        )


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def geotag_field_widget(field, request):
    return FieldWidget(field, GeotagWidget(request))


GeotagFieldWidget = geotag_field_widget
