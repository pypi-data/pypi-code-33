from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):

    @classmethod
    def list(cls, **params):
        instance = cls()
        r = instance.get_request(endpoint='%ss' %instance.class_url(),
                                 **params)
        return instance.parse_json(r)
