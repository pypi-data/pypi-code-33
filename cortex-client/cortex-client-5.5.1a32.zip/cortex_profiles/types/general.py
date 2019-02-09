from typing import List

from attr import attrs

FindQuery = dict
AggregateQuery = List[dict]
OrderedList = List


@attrs(frozen=True, auto_attribs=True)
class CortexProperties(object):
    jwt_token:str
    api_endpoint:str="https://api.cortex.insights.ai"
    environmentId:str="cortex/default"


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
