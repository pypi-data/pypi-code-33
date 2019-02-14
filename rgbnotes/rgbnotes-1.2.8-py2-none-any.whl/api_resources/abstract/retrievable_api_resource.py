from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract.api_resource import APIResource


class RetrievableAPIResource(APIResource):

    @classmethod
    def retrieve(cls, _id=None):
        instance = cls()
        r = instance.get_request(endpoint=instance.class_url(),
                                 id=_id)

        return instance.parse_json(r)
