from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):

    @classmethod
    def list(cls, **params):
        instance = cls()
        class_url = instance.class_url()
        plural_url = '{}es'.format(class_url) if class_url.endswith('s') else '{}s'.format(class_url)
        r = instance.get_request(endpoint=plural_url,
                                 **params)
        return instance.parse_json(r)
