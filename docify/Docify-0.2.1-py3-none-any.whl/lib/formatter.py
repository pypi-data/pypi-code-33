import re
from copy import deepcopy

from docify.lib.document import Document
from docify.lib.components import Component, Element


class Formatter(object):
    '''Abstract class for formatter. Do not use it directly.

    :param Document document: Document to format.
    '''

    @classmethod
    def handlers(cls):
        return {
            str: lambda x: re.sub(r'((([_*]).+?\3[^_*]*)*)([_*])', '\g<1>\\\\\g<4>', x)
        }

    def __init__(self, document):
        self.doc = self.format(deepcopy(document))

    @classmethod
    def format(cls, obj):
        '''Parse and format an object.

        :param Component|Document obj: Object to format.
        '''

        return cls.handlers().get(type(obj), str)(obj)

    @classmethod
    def f(cls, obj):
        '''An alias to format()'''
        return cls.format(obj)

    def __str__(self):
        return self.doc
