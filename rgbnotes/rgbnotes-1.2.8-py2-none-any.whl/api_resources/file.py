from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import ListableAPIResource


class File(ListableAPIResource):

    OBJECT_NAME = 'file'

    @classmethod
    def create(cls, file, **params):
        instance = cls()
        r = instance.post_request(data=params,
                                  files={'file':file},
                                  endpoint='%s_create' %instance.class_url())
        return instance.parse_json(r)
