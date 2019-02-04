from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import CreateableAPIResource
from rgbnotes.api_resources.abstract import ListableAPIResource


class Asset(ListableAPIResource, CreateableAPIResource):

    OBJECT_NAME = 'asset'

    @classmethod
    def version(cls, **params):
        instance = cls()
        r = instance.get_request(endpoint='%s_versions' %cls.class_url(), 
                                 **params)        

        return instance.parse_json(r)
