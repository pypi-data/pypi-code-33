from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract.api_resource import APIResource


class DeletableAPIResource(APIResource):

    @classmethod
    def delete(cls, _id):
        instance = cls()
        r = instance.post_request(data={'id':_id},
                                  endpoint='%s_delete' %instance.class_url())
        return instance.parse_json(r)
