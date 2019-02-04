from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import ListableAPIResource
from rgbnotes.api_resources.abstract import DeletableAPIResource
from rgbnotes.api_resources.abstract import UpdateableAPIResource


class Webhook(ListableAPIResource, DeletableAPIResource, UpdateableAPIResource):

    OBJECT_NAME = 'webhook'
