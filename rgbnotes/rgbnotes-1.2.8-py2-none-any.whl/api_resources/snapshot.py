from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import ListableAPIResource
from rgbnotes.api_resources.abstract import RetrievableAPIResource


class Snapshot(RetrievableAPIResource, ListableAPIResource):

    OBJECT_NAME = 'snapshot'
