class Document(object):
    '''The base document object

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
        '''Adds a component in the doc

        :param Component component: Component to be added'''

        component.setparent(self)
        self.components.append(component)
