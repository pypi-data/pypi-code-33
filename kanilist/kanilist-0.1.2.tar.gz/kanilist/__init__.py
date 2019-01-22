"""kanilist - """

__version__ = '0.1.2'
__author__ = 'fx-kirin <fx.kirin@gmail.com>'
__all__ = ['get_attribute', 'get_diff', 'is_unique']


def get_attribute(list_: list, attribute: str):
    return [getattr(l, attribute) for l in list_]


def get_diff(list1: list, list2: list):
    output1 = [l for l in list1 if l not in list2]
    output2 = [l for l in list2 if l not in list1]
    return output1, output2


def is_unique(list_: list):
    return len(list_) == len(set(list_))
