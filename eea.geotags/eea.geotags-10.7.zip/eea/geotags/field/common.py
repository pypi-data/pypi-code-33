import logging
import json

from zope.interface import noLongerProvides
from zope.interface import alsoProvides
from zope.component import queryAdapter


from eea.geotags.interfaces import IGeoTags
from eea.geotags.interfaces import IGeoTagged

logger = logging.getLogger('eea.geotags.field')


def json2list(geojson, attr='description'):
    """ Util function to extract human readable geo tags from geojson struct
    """
    if not geojson:
        return

    if not isinstance(geojson, dict):
        try:
            value = json.loads(geojson)
        except Exception, err:
            logger.exception(err)
            return
    else:
        value = geojson

    features = value.get('features', [])
    if not features:
        return

    for feature in features:
        properties = feature.get('properties', {})
        data = properties.get(attr, properties.get('description', ''))
        if data:
            yield data
        else:
            yield properties.get('title', '')


def json2string(geojson, attr='description'):
    """ Util method to extract human readable geo tag from geojson struct
    """
    items = json2list(geojson, attr)
    for item in items:
        return item
    return ''


def json2items(geojson, key="title", val="description"):
    """ Util method to extract dict like items geo tags from geojson struct
    """
    if not geojson:
        return

    if not isinstance(geojson, dict):
        try:
            value = json.loads(geojson)
        except Exception, err:
            logger.exception(err)
            return
    else:
        value = geojson

    features = value.get('features', [])
    if not features:
        return

    for feature in features:
        properties = feature.get('properties', {})
        key = properties.get(key, properties.get('title', ''))
        val = properties.get(val, properties.get('description', ''))
        yield (key, val)


def get_tags(context):
    geo = queryAdapter(context, IGeoTags)
    return geo.tags if geo else dict()


def get_json(context):
    """ Get GeoJSON tags from instance annotations using IGeoTags adapter
    """
    tags = get_tags(context)
    return json.dumps(tags)


def set_json(context, value):
    """ Set GeoJSON tags to instance annotations using IGeoTags adapter
    """
    geo = queryAdapter(context, IGeoTags)
    if not geo:
        return

    if not isinstance(value, dict) and value:
        try:
            value = json.loads(value)
        except Exception, err:
            logger.exception(err)
            return

    # remove IGeoTagged if all geotags are removed or provide it
    # if geotags are added
    if not value:
        return

    value_len = len(value.get('features'))
    if not value_len:
        if IGeoTagged.providedBy(context):
            noLongerProvides(context, IGeoTagged)
    else:
        if not IGeoTagged.providedBy(context):
            alsoProvides(context, IGeoTagged)
    geo.tags = value
