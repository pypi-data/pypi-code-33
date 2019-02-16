from collections import namedtuple
from functools import partial
from rossby.default_response import RossbyResponse


response_types = {
    'geo+json': 'application/geo+json',
    'ld+json': 'application/ld+json',
    'dwml': 'application/vnd.noaa.dwml+xml',
    'oxml': 'application/vnd.noaa.obs+xml',
    'capxml': 'application/cap+xml',
    'atom': 'application/atom+xml'
}

APIEndpoint = namedtuple('APIEndpoint', 'endpoint method paginated response param_keys response_type')
DefaultAPIEndpoint = partial(APIEndpoint, paginated=False, response=['geo+json'], param_keys=[],
                             response_type=RossbyResponse)
GETEndpoint = partial(DefaultAPIEndpoint, method='get')
GETPaginatedEndpoint = partial(GETEndpoint, paginated=True)
GETIconEndpoint = partial(GETEndpoint, response_type=None)


api_endpoints = {
    'alerts': {
        'get_all': GETPaginatedEndpoint('alerts', response=['ld+json', 'atom'],
                                        param_keys=['active', 'start', 'end', 'status', 'message_type', 'event',
                                                    'code', 'region_type', 'point', 'region', 'area', 'zone', 'urgency',
                                                    'severity', 'certainty', 'limit']),
        'active': GETPaginatedEndpoint('alerts/active', response=['ld+json', 'atom'],
                                       param_keys=['status', 'message_type', 'event',
                                                   'code', 'region_type', 'point', 'region', 'area', 'zone', 'urgency',
                                                   'severity', 'certainty', 'limit']),
        'by_id': GETEndpoint('alerts/{id}', response=['geo+json', 'ld+json', 'capxml']),
        'types': GETEndpoint('alerts/types', response=['ld+json']),
        'active_count': GETEndpoint('alerts/active/count', response=['ld+json']),
        'active_by_zone': GETEndpoint('alerts/active/zone/{zone_id}', response=['ld+json', 'atom']),
        'active_by_area': GETEndpoint('alerts/active/area/{area}', response=['ld+json', 'atom']),
        'active_by_region': GETEndpoint('alerts/active/region/{region}', response=['ld+json', 'atom'])
    },
    'glossary': {
        'get': GETEndpoint('glossary/', response=['geo+json'])
    },
    'gridpoints': {
        'point': GETEndpoint('gridpoints/{office_id}/{lon},{lat}', response=['geo+json', 'ld+json']),
        'forecast': GETEndpoint('gridpoints/{office_id}/{lon},{lat}/forecast', response=['geo+json', 'ld+json'],
                                param_keys=['units']),
        'hourly_forecast': GETEndpoint('gridpoints/{office_id}/{lon},{lat}/forecast/hourly',
                                       response=['geo+json', 'ld+json'], param_keys=['units']),
        'stations': GETEndpoint('gridpoints/{office_id}/{lon},{lat}/stations', response=['geo+json', 'ld+json'])
    },
    'icons': {
        'all': GETEndpoint('icons'),
        'static_icon': GETIconEndpoint('icons/{set}/{time}/{condition}', param_keys=['size', 'fontsize']),
        'transition_icon': GETIconEndpoint('icons/{set}/{time}/{first_condition}/{second_condition}',
                                           param_keys=['size', 'fontsize'])
    },
    'thumbnails': {
        'get_by_area': GETEndpoint('thumbnails/satellite/{area}')
    },
    'stations': {
        'get_all': GETEndpoint('stations', response=['geo+json', 'ld+json'], param_keys=['id', 'state', 'limit']),
        'by_id': GETEndpoint('stations/{station_id}', response=['geo+json', 'ld+json']),
        'observations': GETEndpoint('stations/{station_id}/observations', response=['geo+json', 'ld+json'],
                                    param_keys=['start', 'end', 'limit']),
        'latest_observation': GETEndpoint('stations/{station_id}/observations/latest',
                                          response=['geo+json', 'ld+json'], param_keys=['require_qc']),
        'observation_by_time': GETEndpoint('stations/{station_id}/observations/{time}',
                                           response=['geo+json', 'ld+json']),
        'radar': GETEndpoint('stations/radar', response=['geo+json', 'ld+json']),
        'radar_by_id': GETEndpoint('stations/radar/{station_id}', response=['geo+json', 'ld+json'])
    },
    'offices': {
        'by_id': GETEndpoint('offices/{office_id}', response=['ld+json']),
        'headline_by_id': GETEndpoint('offices/{office_id}/headlines/{headline_id}', response=['ld+json']),
        'headlines': GETEndpoint('offices/{office_id}/headlines', response=['ld+json'])
    },
    'points': {
        'get_point': GETEndpoint('points/{point}', response=['geo+json', 'ld+json']),
        'get_stations': GETEndpoint('points/{point}/stations', response=['geo+json', 'ld+json']),
        'forecast': GETEndpoint('points/{point}/forecast', response=['geo+json', 'ld+json', 'dwml']),
        'hourly_forecast': GETEndpoint('points/{point}/forecast/hourly', response=['geo+json', 'ld+json']),
    },
    'products': {
        'get': GETEndpoint('products', response=['ld+json'],
                           param_keys=['location', 'start', 'end', 'office', 'wmoid', 'type', 'limit']),
        'locations': GETEndpoint('products/locations', response=['ld+json']),
        'types': GETEndpoint('products/types', response=['ld+json']),
        'by_id': GETEndpoint('products/{product_id}', response=['ld+json']),
        'by_type': GETEndpoint('products/types/{type_id}', response=['ld+json']),
        'type_locations': GETEndpoint('products/types/{type_id}/locations', response=['ld+json']),
        'location_types': GETEndpoint('products/locations/{location_id}/types', response=['ld+json']),
        'by_type_and_location': GETEndpoint('products/types/{type_id}/locations/{location_id}', response=['ld+json'])
    },
    'zones': {
        'get': GETEndpoint('zones', param_keys=['id', 'area', 'region', 'type', 'point', 'include_geometry', 'effective']),
        'by_type': GETEndpoint('zones/{type}', response=['geo+json', 'ld+json'],
                               param_keys=['id', 'area', 'region', 'type', 'point', 'include_geometry', 'effective']),
        'by_type_and_zone_id': GETEndpoint('zones/{type}/{zone_id}', response=['geo+json', 'ld+json'],
                                           param_keys=['effective']),
        'zone_type_forecast': GETEndpoint('zones/{type}/{zone_id}/forecast', response=['geo+json', 'ld+json']),
        'forecast_observations': GETEndpoint('zones/forecast/{zone_id}/observations', response=['geo+json', 'ld+json'],
                                             param_keys=['start', 'end', 'limit']),
        'station_forecasts': GETEndpoint('zones/forecast/{zone_id}/stations', response=['geo+json', 'ld+json'])
    }
}
