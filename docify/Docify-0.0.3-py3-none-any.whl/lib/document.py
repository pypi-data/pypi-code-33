class Document(object):
    '''The base document object.
    It can be passed as input to separate formatters which can parse
    it into various formats.

    Example usage: ::

        doc = Document(Span('im a span !'))
        print(HTML(doc))
        print(Markdown(doc))
        print(Whatever(doc))

    :param Component[] components: Components to be added in the document'''

    def __init__(self, *components):
        self.components = []
        self.depth = 0
        for c in components:
            self.add(c)

    def __str__(self):
        return '\n\n'.join(map(str, self.components))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)

    def add(self, component):
        '''Adds a component in the doc.

        :param Component component: Component to be added'''

        component.setparent(self)
        self.components.append(component)
