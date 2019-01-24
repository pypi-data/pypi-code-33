from copy import deepcopy


class Component(object):
    '''An abstract class for any component. Do not use this class directly.

    :param Component[] children: Single or collection of child components
        to be wrapped by this component.
    '''

    def __init__(self, *children):
        self.children = []
        self.parent = None
        self.depth = 0
        for c in children:
            self.add(c)

    def __str__(self):
        return '\n'.join(map(str, self.children))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)

    def add(self, child):
        '''Appends a component or an element as it's child.

        :param Component child: The child object to be added.'''

        if isinstance(child, Component):
            child.setparent(self)
        self.children.append(child)

    def setdepth(self, depth):
        '''Sets the depth of this component
        and also updates depths of it's children.

        :param int depth: depth to set.'''

        self.depth = depth
        for c in self.children:
            isinstance(c, Component) and c.setdepth(depth+1)

    def setparent(self, parent):
        '''Sets the reference to it's parent object
        and also updates it's depth based on parent's depth.

        :param Component|Document parent: Object to set as parent.'''

        self.parent = parent
        self.setdepth(parent.depth + 1)


class Section(Component):
    '''Section. Similar to <section></section>
    It joins all it's children with with new-line equivalent.

    Example usage: ::

        s = Section('a', 'b', 'c')
        # Result: <section>a<br />b<br />c</section>
    '''

    def __str__(self):
        return '{}\n\n'.format('\n'.join(map(str, self.children)))


class Span(Component):
    '''Similar to <span></span>.
    It joins all it's children without any separator.
    So when we do Element() + Element(), we get Span(Element(), Element()).
    Supports ``+`` operator to return new `Span` with added child.

    Example usage: ::

        s = Span('im a span.', Nbsp(), 'Hail Docify!')
        # Result: 'im a span. Hail Docify!'

    Example addition: ::

        Span('Hail') + Nbsp() + B('Docify') + I('!')
        # Result: Span('Hail', Nbsp(), B('Docify'), I('!'))
        # Result: 'Hail <b>Docify</b><i>!</i>'
    '''

    def __str__(self):
        return ''.join(map(str, self.children))

    def __add__(self, element):
        obj = deepcopy(self)
        obj.add(element)
        return obj

    def add(self, child):
        '''Appends a component or an element as it's child.

        :param Component child: The child object to be added.'''

        if isinstance(child, Component):
            child.setparent(self)
        self.children.append(child)


class List(Component):
    '''Abstract class for ordered and unordered list.
    Do not use it directly.

    :param Component[] children: `ListItem` or `List` to add as children.:
    '''

    child_idx = '{index}.'

    def __init__(self, *children):
        self.level = 0
        self.index = 0
        super(List, self).__init__(*children)

    def setlevel(self, level):
        '''Sets relative depth from parent List
        in case it's nested into another List. Also updates it's children.

        :param int level: Level to set.
        '''

        self.level = level
        for c in self.children:
            isinstance(c, List) and c.setlevel(level+1)

    def setindex(self, index):
        '''Sets the index in case it's nested in another List.

        :param int index: Index to set.
        '''
        self.index = index

    def add(self, child):
        '''Add a child to the list.

        :param List|ListItem child: Adds a child object
        '''

        child.setparent(self)
        child.setindex(self.child_idx.format(
            index=(len(self.children) + 1)))
        if isinstance(child, List):
            child.setlevel(self.level + 1)
        self.children.append(child)


class OrderedList(List):
    '''OrderedList. Similar to <ol></ol>.

    Example usage: ::

        ol = Ol(Li('item 1'), Li('item 2'), Ol(Li('item 2.1')))
    '''
    pass


class UnorderedList(List):
    '''UnorderedList. Similar to <ul></ul>.

    Example usage: ::
        ul = Ul(Li('item 1'), Li('item 2'), Ul(Li('item 2.1')))
    '''

    child_idx = '*'


class Element(Component):
    '''An abstract class for any single element. Do not use it directly.
    Supports ``+`` operator to return new `Span` with added component.

    :param Element element: Element to be wrapped.

    Example addition: ::

        I('Hail') + Nbsp() + B('Docify!')
        # Result: Span(I('Hail'), Nbsp(), B('Docify!'))
    '''

    txt = '{element}'

    def __init__(self, element=''):
        super(Element, self).__init__(element)
        self.element = self.children[0]

    def __str__(self):
        return self.txt.format(**self.__dict__)

    def __repr__(self):
        return '\n{}({})'.format(self.__class__.__name__, self)

    def __add__(self, element):
        span = Span(self)
        span.setparent(self.parent)
        span.add(element)
        return span


class Header(Element):
    '''Header, Do not use it directly. It's supposed to be an abstract class'''

    header_type = 1
    txt = '# {element}\n'


class Header1(Header):
    '''Header1. Similar to <h1></h1>'''

    header_type = 1
    txt = '{element}\n====================\n'


class Header2(Header):
    '''Header2. Similar to <h2></h2>'''

    header_type = 2
    txt = '{element}\n--------------------\n'


class Header3(Header):
    '''Header3. Similar to <h3></h3>'''

    header_type = 3
    txt = '### {element}\n'


class Header4(Header):
    '''Header4. Similar to <h4></h4>'''

    header_type = 4
    txt = '#### {element}\n'


class Header5(Header):
    '''Header5. Similar to <h5></h5>'''

    header_type = 5
    txt = '##### {element}\n'


class Header6(Header):
    '''Header6. Similar to <h6></h6>'''

    header_type = 6
    txt = '###### {element}\n'


class Italic(Element):
    '''Italic. Similar to <i></i>'''

    txt = '*{element}*'


class Bold(Element):
    '''Bold. Similar to <b></b>'''

    txt = '**{element}**'


class HorizontalRule(Element):
    '''Horizontal Rule. Similar to <hr/>'''

    txt = ('-' * 50) + '\n'


class Break(Element):
    '''Break. Similar to <br />
    Try to avoid using it as much as possible as different
    formats interpretes it differently. Use `Section` instead.
    '''

    txt = '\n'


class Anchor(Element):
    '''Anchor. Similar to <a></a>

    :param Element element: Element to be wrapped.
    :param str href: Target URL.

    Example usage: ::

        a = A('Google', href='https://google.com')
    '''

    txt = '[{element}]({href})'

    def __init__(self, element, href):
        super(Anchor, self).__init__(element)
        self.href = href


class Image(Element):
    '''Image. Similar to <img/>

    :param str alt: Alternate text
    :param str src: Source file

    Example usage: ::

        i = Img(src='https://img.shields.io/badge/docify-image_test-green.svg', alt='Image test')
    '''

    txt = '![{alt}]({src})'

    def __init__(self, alt, src):
        super(Image, self).__init__()
        self.alt = alt
        self.src = src


class Pre(Element):
    '''Pre. Similar to <pre></pre>'''

    txt = '```\n{element}\n```\n'


class Code(Element):
    '''Code. Similar to <code></code>'''

    def __str_(self):
        if isinstance(self.parent, Pre):
            return self.element
        return '``{}``'.format(self.element)


class Blockquote(Element):
    '''Blockquote. Similar to <blockquote></blockquote>'''

    txt = '> {element}\n'


class Del(Element):
    '''Del. Similar to <del></del>'''

    txt = '~~{element}~~'


class ListItem(Element):
    '''ListItem. Similar to <li></li>

    :param Element element: Element to be wrapped.
    '''

    def __init__(self, element=''):
        super(ListItem, self).__init__(element)
        self.index = '*'

    def setindex(self, index):
        '''Sets index.

        :param int index: Index to set.
        '''
        self.index = index

    def __str__(self):
        return '{}{} {}'.format(
            (' ' * self.parent.level * 3), self.index, self.element)


class NoBreakSpace(Element):
    '''NoBreakSpace. Similar to &nbsp;'''

    txt = ' '


# Aliases
Ol = OrderedList
Ul = UnorderedList
Hr = HorizontalRule
Br = Break
Img = Image
A = Anchor
Li = ListItem
H1 = Header1
H2 = Header2
H3 = Header3
H4 = Header4
H5 = Header5
H6 = Header6
B = Bold
Strong = Bold
I = Italic
Em = Italic
Nbsp = NoBreakSpace
