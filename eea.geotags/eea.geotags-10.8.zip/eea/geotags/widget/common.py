import json

from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from eea.geotags.controlpanel.interfaces import IGeotagsSettings

STR_PF = 'portal_factory'

URL_DIALOG = '@@eea.geotags.dialog'
URL_SIDEBAR = '@@eea.geotags.sidebar'
URL_BASKET = '@@eea.geotags.basket'
URL_JSON = '@@eea.geotags.json'
URL_SUGGESTIONS = '@@eea.geotags.suggestions'
URL_COUNTRY_MAPPING = '@@eea.geotags.mapping'


def get_base_url(request):
    url1 = request.URL1
    portal_factory = STR_PF in url1
    return url1.split(STR_PF)[0] if portal_factory else url1 + '/'


def get_maps_api_key():
    settings = getUtility(IRegistry).forInterface(IGeotagsSettings, False)
    return settings.maps_api_key


def get_js_props(multiline, field_id, field_name, base_url, geojson):
    # type: (int, str, str, str, str) -> str
    return json.dumps(dict(
        id=field_id,
        name=field_name.replace('.', '\\.'),
        # Convert the geojson to python dict so it doesn't get json encoded
        # twice, as this function will return a JSON.
        geojson=json.loads(geojson),  # type: dict
        multiline=multiline,
        basket=base_url + URL_BASKET,
        sidebar=base_url + URL_SIDEBAR,
        dialog=base_url + URL_DIALOG,
        json=base_url + URL_JSON,
        suggestions=base_url + URL_SUGGESTIONS,
        country_mapping=base_url + URL_COUNTRY_MAPPING,
    ))
