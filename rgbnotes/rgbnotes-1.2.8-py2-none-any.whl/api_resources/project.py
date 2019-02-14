from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import CreateableAPIResource
from rgbnotes.api_resources.abstract import DeletableAPIResource
from rgbnotes.api_resources.abstract import ListableAPIResource
from rgbnotes.api_resources.abstract import UpdateableAPIResource


class Project(ListableAPIResource, CreateableAPIResource,
              DeletableAPIResource, UpdateableAPIResource):

    OBJECT_NAME = 'project'
