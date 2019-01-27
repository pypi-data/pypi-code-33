# -*- coding: utf-8 -*-

import pprint

from tests.unittests.mixins.send_payload_mixin import SendPayloadMixin


class BasePayload(SendPayloadMixin, dict):

    TYPES = [
        'badge',
        'geokret',
        'geokret-type',
        'move',
        'move-type',
        'move-comment',
        'user',
        'news',
        'news-subscription',
        'news-comment',
    ]

    def __init__(self, obj_type, *args, **kwargs):
        self._update_payload_attributes(**kwargs)
        super(BasePayload, self).__init__(*args, **kwargs)

        if obj_type not in self.TYPES:  # pragma: no cover
            raise AttributeError("Invalid Payload type ({})".format(obj_type))
        self.type = obj_type

        self.update({
            "data": {
                "type": obj_type
            }
        })

    def _update_payload_attributes(self, **kwargs):
        if "_url" in kwargs:
            self._url = kwargs.pop('_url')
        if "_url_collection" in kwargs:
            self._url_collection = kwargs.pop('_url_collection')

    def set_id(self, value):
        self['data']['id'] = str(value)
        return self

    def _set_attribute(self, name, value):
        name = name.replace('_', '-')
        if 'attributes' not in self['data']:
            self['data']['attributes'] = {}
        if name not in self['data']['attributes']:
            self['data']['attributes'][name] = {}

        self['data']['attributes'][name] = value
        return self

    def _del_attribute(self, attribute):
        if 'attributes' in self['data']:
            self['data']['attributes'].pop(attribute, None)
        return self

    def _set_relationships(self, relationships, name, obj_id):
        if 'relationships' not in self['data']:
            self['data']['relationships'] = {}
        if relationships not in self['data']['relationships']:
            self['data']['relationships'][relationships] = {}

        self['data']['relationships'][relationships].update({
            'data': {
                'type': name,
                'id': obj_id,
            }
        })
        return self

    def _del_relationships(self, relationships):
        if 'relationships' in self['data']:
            self['data']['relationships'].pop(relationships, None)
        return self

    def _set_relationships_many(self, relationships, name, ids):
        if 'relationships' not in self['data']:  # pragma: no cover
            self['data']['relationships'] = {}
        if relationships not in self['data']['relationships']:
            self['data']['relationships'][relationships] = {}

        datas = []
        for id_ in ids:
            datas.append({
                'type': name,
                'id': id_,
            })
        self['data']['relationships'][relationships]['data'] = datas
        return self

    def blend(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("`blend` is not implemented")

    def set_obj(self, obj):  # pragma: no cover
        raise NotImplementedError("`set_obj` is not implemented")

    def pprint(self):  # pragma: no cover
        pprint.pprint(self)
        return self
