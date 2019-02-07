from copy import deepcopy


class _Component(object):
    '''An abstract class for any component. Do not use this class directly.
    Supports ``+`` operator to return a group of components wrapped inside Span.

    :param dict properties: Extra properties for the component.

    Example addition: ::

        I('Some text') + Nbsp() + 'Some other text'
        # Result: Span(I('Some text'), Nbsp(), 'Some other text')

        I('Some text') + Nbsp() + Span('Some other', 'text')
        # Result: Span('Some text', Nbsp(), 'Some other', 'text')

        Span('Some text') + Nbsp() + Span('Some other text')
        # Result: Span('Some text', Nbsp(), 'Some other text')
    '''

    def __init__(self, **properties):
        self.props = properties
        self.parent = None
        self.depth = 0
        self.prev = None
        self.next = None

    def setparent(self, parent):
        '''Set the parent object.
        Also updates it's depth based on parent's depth.

        :param Component|Document parent: Parent to set.
        '''
        self.parent = parent
        self.setdepth(parent.depth + 1)

    def setnext(self, nxt):
        '''Add reference to previous and next element to support
        doubly linked-list like iteration.

        :param Component nxt: Next component to link.
        '''
        self.next = nxt
        nxt.prev = self

    def setdepth(self, depth):
        '''Set depth of current component.

        :param int depth: depth to set.
        '''
        self.depth = depth

    def __add__(self, component):
        if isinstance(self, Span):
            span = deepcopy(self)
        else:
            span = Span()
            if self.parent is not None:
                span.setparent(self.parent)
            span.add(self)

        if not isinstance(component, Span):
            span.add(component)
        else:
            for c in component.components:
                span.add(c)
        return span


class _Leaf(_Component):
    '''An abstract class for leaf components'''
    pass


class Text(_Leaf):
    '''String objects are automatically wrapped into Text.
    So you don't need to use it directly.

    :param str value: String object to wrap.

    Example: ::

        Document('Some text', 'Some more text')
        # Becomes: Document(Text('Some text'), Text('Some other text'))
    '''

    def __init__(self, value):
        super(Text, self).__init__()
        self.value = str(value)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value.__repr__())


class _Symbol(_Leaf):
    '''An abstract class for all primitive symbols. Do not use it directly.'''

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class NoBreakSpace(_Symbol):
    '''NoBreakSpace. Similar to &nbsp;'''
    pass


class Break(_Symbol):
    '''Break. Similar to <br />'''
    pass


class HorizontalRule(_Symbol):
    '''HorizontalRule. Similar to <hr />'''
    pass


class Anchor(_Leaf):
    '''Anchor. Similar to <a></a>.

    :param str value: Text to display.
    :param str href: URL link.

    Example usage: ::

        Anchor('Some link', href='https://some.link.com')
    '''

    def __init__(self, value, href, **kwargs):
        super(Anchor, self).__init__(href=href, **kwargs)
        self.value = value

    def __repr__(self):
        return '{}({}, href={})'.format(
            self.__class__.__name__, self.value.__repr__(),
            self.props['href'].__repr__())


class Image(_Leaf):
    '''Image. Similar to <img />.

    :param str src: Source of image.
    :param str alt: Alternate text to display.

    Example usage: ::

        Image(src='https://some.source.com/someimage.png', alt='Some text')
    '''

    def __init__(self, src, alt, **kwargs):
        super(Image, self).__init__(src=src, alt=alt, **kwargs)

    def __repr__(self):
        return '{}(src={}, alt={})'.format(
            self.__class__.__name__, self.props['src'].__repr__(),
            self.props['alt'].__repr__())


class _Composite(_Component):
    '''Abstract for components with multiple child. Do not use it directly.

    :param list components: Components to add.
    '''

    def __init__(self, *components, **kwargs):
        super(_Composite, self).__init__(**kwargs)
        self.components = []
        for c in components:
            self.add(c)

    def add(self, component):
        '''Add a new component as child.

        :param Component component: Component to add.
        '''
        if not isinstance(component, _Component):
            component = Text(component)
        component.setparent(self)

        if len(self.components) > 0:
            self.components[-1].setnext(component)

        self.components.append(component)

    def setdepth(self, depth):
        '''Overwriting setdepth method.'''

        self.depth = depth
        for c in self.components:
            c.setdepth(self.depth + 1)

    def __repr__(self):
        return '{}(\n{}{})'.format(
            self.__class__.__name__, ' ' * (self.depth + 1) * 4,
            ('\n' + (' ' * (self.depth + 1) * 4)).join(map(str, self.components)))


class _Header(_Composite):
    '''Header, Do not use it directly. It's supposed to be an abstract class'''
    pass


class Header1(_Header):
    '''Header1. Similar to <h1></h1>'''
    pass


class Header2(_Header):
    '''Header2. Similar to <h2></h2>'''
    pass


class Header3(_Header):
    '''Header3. Similar to <h3></h3>'''
    pass


class Header4(_Header):
    '''Header4. Similar to <h4></h4>'''
    pass


class Header5(_Header):
    '''Header5. Similar to <h5></h5>'''
    pass


class Header6(_Header):
    '''Header6. Similar to <h6></h6>'''
    pass


class Footer(_Composite):
    '''Footer. Similar to <footer></footer>'''
    pass


class Small(_Composite):
    '''Small. Similar to <small></small>'''
    pass


class Cite(_Composite):
    '''Cite. Similar to <cite></cite>'''
    pass


class Italic(_Composite):
    '''Italic. Similar to <i></i>'''
    pass


class Bold(_Composite):
    '''Bold. Similar to <b></b>'''
    pass


class Blockquote(_Composite):
    '''Blockquote. Similar to <blockquote></blockquote>'''
    pass


class Pre(_Composite):
    '''Pre. Similar to <pre></pre>'''
    pass


class Code(_Composite):
    '''Code. Similar to <code></code>'''
    pass


class Del(_Composite):
    '''Del. Similar to <del></del>'''
    pass


class Section(_Composite):
    '''Section. Similar to <section></section>.

    Example usage: ::

        Section(I('Some text'), B('Some other text'))
    '''
    pass


class Paragraph(_Composite):
    '''Paragraph. Similar to <p></p>.

    Example usage: ::

        P(I('Some text'), Nbsp(), B('Some other text'))
    '''
    pass


class Span(_Composite):
    '''Span. Similar to <span></span>.

    Example usage: ::

        Span('Some text', 'Some other text')
    '''
    pass


class _List(_Composite):
    '''Abstract class for ordered and unordered list.
    Do not use it directly.
    '''
    pass


class OrderedList(_List):
    '''OrderedList. Similar to <ol></ol>.

    Example usage: ::

        Ol(Li('item 1'), Li('item 2'), Ol(Li('item 2.1')))
    '''
    pass


class UnorderedList(_List):
    '''UnorderedList. Similar to <ul></ul>.

    Example usage: ::

        Ul(Li('item 1'), Li('item 2'), Ul(Li('item 2.1')))
    '''
    pass


class ListItem(_Composite):
    '''ListItem. Similar to <li></li>.
    It should be used inside OrderedList and UnorderedList only.
    '''
    pass


class Table(_Composite):
    '''Table. Similar to <table></table>.

    Example usage: ::

        Table(
            Tr(Th('header 1'), Th('header 2')),
            Tr(Td('value 1'), Td('value 2')))
    '''
    pass


class TableHeader(_Composite):
    '''TableHeader. Similar to <thead></thead>'''
    pass


class TableRow(_Composite):
    '''TableRow. Similar to <tr></tr>'''
    pass


class TableData(_Composite):
    '''TableData. Similar to <td></td>'''
    pass


# Aliases
Ol = OrderedList
Ul = UnorderedList
Hr = HorizontalRule
Br = Break
Img = Image
A = Anchor
Nbsp = NoBreakSpace
Li = ListItem
H1 = Header1
H2 = Header2
H3 = Header3
H4 = Header4
H5 = Header5
H6 = Header6
P = Paragraph
B = Bold
Strong = Bold
I = Italic
Em = Italic
Th = TableHeader
Tr = TableRow
Td = TableData
