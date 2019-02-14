from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract.api_resource import APIResource


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, **params):
        instance = cls()
        r = instance.post_request(data=params,
                                  endpoint='%s_create' %instance.class_url())
        return instance.parse_json(r)
