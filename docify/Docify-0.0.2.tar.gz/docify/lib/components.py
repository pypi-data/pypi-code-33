class Component(object):
    '''An abstract class for any components

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
        '''Appends a component or an element as it's child

        :param Component child: The child object to be added'''

        if isinstance(child, Component):
            child.setparent(self)
        self.children.append(child)

    def setdepth(self, depth):
        self.depth = depth
        if isinstance(self, Element):
            return
        for c in self.children:
            c.setdepth(depth+1)

    def setparent(self, parent):
        self.parent = parent
        self.setdepth(parent.depth + 1)


class Division(Component):
    '''Division. Use it when you want components to be in a single section'''

    def __add__(self, component):
        div = Division(*self.children)
        div.setparent(self.children[0].parent)
        if isinstance(component, Div):
            for c in component.children:
                div.add(c)
        else:
            div.add(component)
        return div

    def __str__(self):
        return ''.join(map(str, self.children))


class List(Component):
    '''Abstract class for ordered and unordered list. Do not use it directly'''

    child_idx = '{index}.'

    def __init__(self, *children):
        self.level = 0
        self.index = 0
        super(List, self).__init__(*children)

    def setlevel(self, level):
        self.level = level
        for c in self.children:
            isinstance(c, List) and c.setlevel(level+1)

    def setindex(self, index):
        self.index = index

    def add(self, child):
        '''Add a child to the list'''
        child.setparent(self)
        child.setindex(self.child_idx.format(
            index=(len(self.children) + 1)))
        if isinstance(child, List):
            child.setlevel(self.level + 1)
        self.children.append(child)


class OrderedList(List):
    '''OrderedList. Similar to <ol></ol>'''
    pass


class UnorderedList(List):
    '''UnorderedList. Similar to <ul></ul>'''

    child_idx = '*'


class Element(Component):
    '''An abstract class for any single element

    :param Element element: Element to be wrapped
    '''

    txt = '{element}'

    def __init__(self, element=''):
        super(Element, self).__init__(element)
        self.element = self.children[0]

    def __str__(self):
        return self.txt.format(**self.__dict__)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)

    def __add__(self, o):
        if isinstance(o, Div):
            return Div(self, *o.elements)
        return Div(self, o)


class Header(Element):
    '''Header, Do not use it directly. It's supposed to be an abstract class'''

    header_type = 1
    txt = '# {element}'


class Header1(Header):
    '''Header1. Similar to <h1></h1>'''

    header_type = 1
    txt = '{element}\n===================='


class Header2(Header):
    '''Header2. Similar to <h2></h2>'''

    header_type = 2
    txt = '{element}\n--------------------'


class Header3(Header):
    '''Header3. Similar to <h3></h3>'''

    header_type = 3
    txt = '### {element}'


class Header4(Header):
    '''Header4. Similar to <h4></h4>'''

    header_type = 4
    txt = '#### {element}'


class Header5(Header):
    '''Header5. Similar to <h5></h5>'''

    header_type = 5
    txt = '##### {element}'


class Header6(Header):
    '''Header6. Similar to <h6></h6>'''

    header_type = 6
    txt = '###### {element}'


class Italic(Element):
    '''Italic. Similar to <i></i>'''

    txt = '*{element}*'


class Bold(Element):
    '''Bold. Similar to <b></b>'''

    txt = '**{element}**'


class Break(Element):
    '''Break. Similar to <br />'''

    txt = '\n'


class HorizontalRule(Element):
    '''Horizontal Rule. Similar to <hr/>'''

    txt = '-' * 50


class Span(Element):
    '''Division. Similar to <span></span>'''

    txt = '{element}'


class Anchor(Element):
    '''Anchor. Similar to <a></a>'''

    txt = '[{element}]({href})'

    def __init__(self, element, href):
        super(Anchor, self).__init__(element)
        self.href = href


class Image(Element):
    '''Image. Similar to <img/>'''

    txt = '![{alt}]({src})'

    def __init__(self, alt, src):
        super(Image, self).__init__()
        self.alt = alt
        self.src = src


class Pre(Element):
    '''Pre. Similar to <pre></pre>'''

    txt = '```\n{element}\n```'


class Code(Element):
    '''Code. Similar to <code></code>'''

    txt = '``{element}``'


class Blockquote(Element):
    '''Blockquote. Similar to <blockquote></blockquote>'''

    txt = '> {element}'


class Del(Element):
    '''Del. Similar to <del></del>'''

    txt = '~~{element}~~'


class ListItem(Element):
    '''ListItem. Similar to <li></li>'''

    def __init__(self, element=''):
        super(ListItem, self).__init__(element)
        self.index = '*'

    def setindex(self, index):
        self.index = index

    def __str__(self):
        return '{}{} {}'.format(
            (' ' * self.parent.level * 3), self.index, self.element)


class NoBreakSpace(Element):
    '''NoBreakSpace. Similar to &nbsp;'''

    txt = ' '


# Aliases
Div = Division
Ol = OrderedList
Ul = UnorderedList
Br = Break
Hr = HorizontalRule
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
I = Italic
Nbsp = NoBreakSpace
