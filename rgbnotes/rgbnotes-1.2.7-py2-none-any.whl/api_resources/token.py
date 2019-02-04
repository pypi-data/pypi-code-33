from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import APIResource


class Token(APIResource):

    @classmethod
    def client(cls, **data):

        instance = cls()
        instance.get_token(project=False, **data)

    @classmethod
    def project(cls, **data):

        instance = cls()
        instance.get_token(project=True, **data)
