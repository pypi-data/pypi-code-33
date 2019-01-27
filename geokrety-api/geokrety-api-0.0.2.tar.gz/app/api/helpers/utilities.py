# -*- coding: utf-8 -*-

from app.api.helpers.exceptions import UnprocessableEntity


def dasherize(text):
    return text.replace('_', '-')


def require_relationship(resource_list, data):
    for resource in resource_list:
        if resource not in data:
            raise UnprocessableEntity("A valid relationship with {} resource is required".format(resource),
                                      {'pointer': '/data/relationships/{}'.format(resource)})


def has_relationships(json_data, relation):
    return json_data is not None and \
        'data' in json_data and \
        'relationships' in json_data['data'] and \
        relation in json_data['data']['relationships'] and \
        'data' in json_data['data']['relationships'][relation] and \
        'id' in json_data['data']['relationships'][relation]['data']
