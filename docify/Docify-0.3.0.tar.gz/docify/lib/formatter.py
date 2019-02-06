import re
from copy import deepcopy

from docify import Document, components as c


class Formatter(object):
    '''Abstract class for formatter. Do not use it directly.

    :param Document document: Document to format.
    :param bool cite: Whether to add the grumpy citation. Default is True.
    '''

    def __init__(self, document, cite=True):
        self.handlers = {}
        raw_doc = deepcopy(document)
        if cite:
            raw_doc.add(c.Hr())
            raw_doc.add(c.Footer(c.P(c.Small(c.Cite(
                'This document was generated with ',
                c.A('Docify', 'https://github.com/rapidstack/Docify'),
                '.')))))
        self.update_handlers()
        self.doc = self.format(raw_doc)

    def handle(self, *items):
        '''handle decorator. Register a handler for given item.
        
        :param list items: List of items to handle.

        Example usage: ::

            @MyFormatter.handle(Document)
            def handle_doc(state, doc):
                return str(doc)
        '''
        return lambda func: [self.handlers.update({i: func}) for i in items]
    
    def update_handlers(self):
        '''Update handlers. Called before format.'''
        pass

    def format(self, obj):
        '''Parse and format an object.

        :param Component|Document obj: Object to format.
        '''
        otype = type(obj)
        if otype not in self.handlers:
            return str(obj)
        return self.handlers[otype](self, obj)

    def __repr__(self):
        return self.doc


# Alias for format method
Formatter.f = Formatter.format