from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract.api_resource import APIResource


class UpdateableAPIResource(APIResource):

    @classmethod
    def modify(cls, _id, **data):
        data.update({'id':_id})
        instance = cls()
        r = instance.post_request(data=data,
                                  endpoint='%s_edit' %instance.class_url())
        return instance.parse_json(r)
