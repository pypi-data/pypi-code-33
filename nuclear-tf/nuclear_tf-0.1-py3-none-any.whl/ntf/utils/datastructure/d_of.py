from collections import defaultdict
from abc import ABCMeta


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class d_of_something(defaultdict):
    __metaclass__ = ABCMeta
    __getattr__ = dict.__getitem__


#############################

class d_of_l(d_of_something):
    def __init__(self):
        super().__init__(list)
