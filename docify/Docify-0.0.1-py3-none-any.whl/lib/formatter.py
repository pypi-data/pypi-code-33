import re
from copy import deepcopy

from docify.lib.document import Document
from docify.lib.components import Component, Element


class Formatter(object):
    '''A generic formatter'''

    handlers = {}

    def __init__(self, document):
        self.handlers = self.handlers
        self.doc = self.format(deepcopy(document))

    @classmethod
    def format(cls, obj):
        if isinstance(obj, Element):
            if isinstance(obj.element, str):
                obj.element = cls.escape(obj.element)
        elif isinstance(obj, Document):
            obj.components = map(cls.format, obj.components)
        elif isinstance(obj, Component):
            obj.children = map(cls.format, obj.children)

        t = type(obj)
        if t in cls.handlers:
            obj = cls.handlers[t](obj)

        return str(obj)

    @classmethod
    def f(cls, obj):
        '''An alias fo format'''
        return cls.format(obj)

    @classmethod
    def escape(cls, txt):
        '''Escape logic'''
        return re.sub(r'((([_*]).+?\3[^_*]*)*)([_*])', '\g<1>\\\\\g<4>', txt)

    def handle(self, component_type, handler):
        self.handlers[component_type] = handler

    def __str__(self):
        return self.doc
