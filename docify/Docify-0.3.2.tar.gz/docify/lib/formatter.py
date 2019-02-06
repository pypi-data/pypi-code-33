from copy import deepcopy

from docify import components as c


class Formatter(object):
    '''Abstract class for formatter. Do not use it directly.

    :param Document document: Document to format.
    :param bool cite: Whether to add the grumpy citation. Default is True.

    Example usage: ::

        class MyFormatter(Formatter):
            @self.handle(Span, Paragraph)
            def handle_span_and_paragraph(self, obj):
                return str(obj)
    '''

    def __init__(self, document, cite=True):
        self.handlers = {}
        self.doc = deepcopy(document)
        if cite:
            self.doc.add(c.Hr())
            self.doc.add(c.Footer(c.P(c.Small(c.Cite(
                'This document was generated with ',
                c.A('Docify', 'https://github.com/rapidstack/Docify'),
                '.')))))

    def handle(self, *items):
        '''Handle decorator. Register a handler for given items.

        :param list items: List of items to handle.
        '''
        return lambda func: [self.handlers.update({i: func}) for i in items]

    def update_handlers(self):
        '''Update handlers. Called by render() before
        performing format operation.
        '''
        pass

    def format(self, obj):
        '''Parse and format an object using appropriate handler.
        If handler is not found, it will use `str`.

        :param Component|Document obj: Object to format.
        '''
        otype = type(obj)
        if otype not in self.handlers:
            return str(obj)
        return self.handlers[otype](self, obj)

    def render(self):
        '''Renders the formatted document. Called by __repr__.'''
        self.update_handlers()
        return self.format(self.doc)

    def __repr__(self):
        return self.render()


# Alias for format method
Formatter.f = Formatter.format
