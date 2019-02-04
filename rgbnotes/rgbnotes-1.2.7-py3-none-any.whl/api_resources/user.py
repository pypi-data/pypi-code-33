from __future__ import absolute_import, division, print_function

from rgbnotes.api_resources.abstract import CreateableAPIResource
from rgbnotes.api_resources.abstract import ListableAPIResource
from rgbnotes.api_resources.abstract import UpdateableAPIResource
from rgbnotes.api_resources.abstract import DeletableAPIResource


class User(ListableAPIResource, CreateableAPIResource):

    OBJECT_NAME = 'user'


    
