import cgi

from docify.lib.formatter import Formatter
from docify import Document, components as c


DOC_TMPL = '''\
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Docify Document</title>
    </head>
    <body>
        <div id="container">
            {}
        </div>
    </body>
</html>
'''


class HTML(Formatter):
    '''HTML formatter to format document into plain HTML.'''

    def __init__(self, *args, **kwargs):
        super(HTML, self).__init__(*args, **kwargs)
        self.tmpl = DOC_TMPL
        self.indent = 4
        self._spacing = 12

    def tag(self, tag, components=[], properties={}):
        attrs = ''
        if len(properties) > 0:
            attrs += ' '
            for k in properties:
                v = properties[k]
                attrs += '{}="{}"'.format(k, v.replace('"', '\\"'))

        if len(components) == 0:
            return '<{0}{1} />'.format(tag, attrs)

        return '<{0}{1}>{2}</{0}>'.format(
            tag, attrs, ''.join([self.f(c) for c in components]))

    def update_handlers(self):
        '''Overriding parent method'''

        super(HTML, self).update_handlers()

        @self.handle(Document)
        def handle_doc(self, obj):
            self._spacing
            return self.tmpl.format(('\n' + (' ' * self._spacing)).join(
                [self.f(c) for c in obj.components]))

        @self.handle(c.Text)
        def handle_text(self, obj):
            return cgi.escape(obj.value)

        @self.handle(c.Nbsp)
        def handle_nbsp(self, obj):
            return '&nbsp;'

        @self.handle(c.Break)
        def handle_br(self, obj):
            return '<br />'

        @self.handle(c.HorizontalRule)
        def handle_hr(self, obj):
            return '<hr />'

        @self.handle(c.Anchor)
        def handle_a(self, obj):
            return self.tag('a', [obj.value], obj.props)

        @self.handle(c.Image)
        def handle_img(self, obj):
            return self.tag('img', [], obj.props)

        @self.handle(c.Header1)
        def handle_h1(self, obj):
            return self.tag('h1', obj.components, obj.props)

        @self.handle(c.Header2)
        def handle_h2(self, obj):
            return self.tag('h2', obj.components, obj.props)

        @self.handle(c.Header3)
        def handle_h3(self, obj):
            return self.tag('h3', obj.components, obj.props)

        @self.handle(c.Header4)
        def handle_h4(self, obj):
            return self.tag('h4', obj.components, obj.props)

        @self.handle(c.Header5)
        def handle_h5(self, obj):
            return self.tag('h5', obj.components, obj.props)

        @self.handle(c.Header6)
        def handle_h6(self, obj):
            return self.tag('h6', obj.components, obj.props)

        @self.handle(c.Footer)
        def handle_footer(self, obj):
            return self.tag('footer', obj.components, obj.props)

        @self.handle(c.Small)
        def handle_small(self, obj):
            return self.tag('small', obj.components, obj.props)

        @self.handle(c.Cite)
        def handle_cite(self, obj):
            return self.tag('cite', obj.components, obj.props)

        @self.handle(c.Italic)
        def handle_i(self, obj):
            return self.tag('i', obj.components, obj.props)

        @self.handle(c.Bold)
        def handle_b(self, obj):
            return self.tag('b', obj.components, obj.props)

        @self.handle(c.Blockquote)
        def handle_blockquote(self, obj):
            return self.tag('blockquote', obj.components, obj.props)

        @self.handle(c.Pre)
        def handle_pre(self, obj):
            return self.tag('pre', obj.components, obj.props)

        @self.handle(c.Code)
        def handle_code(self, obj):
            return self.tag('code', obj.components, obj.props)

        @self.handle(c.Del)
        def handle_del(self, obj):
            return self.tag('del', obj.components, obj.props)

        @self.handle(c.Section)
        def handle_section(self, obj):
            return self.tag('section', obj.components, obj.props)

        @self.handle(c.Paragraph)
        def handle_p(self, obj):
            return self.tag('p', obj.components, obj.props)

        @self.handle(c.Span)
        def handle_span(self, obj):
            return self.tag('span', obj.components, obj.props)

        @self.handle(c.OrderedList)
        def handle_ol(self, obj):
            return self.tag('ol', obj.components, obj.props)

        @self.handle(c.UnorderedList)
        def handle_ul(self, obj):
            return self.tag('ul', obj.components, obj.props)

        @self.handle(c.ListItem)
        def handle_li(self, obj):
            return self.tag('li', obj.components, obj.props)

        @self.handle(c.Table)
        def handle_table(self, obj):
            return self.tag('table', obj.components, obj.props)

        @self.handle(c.TableHeader)
        def handle_th(self, obj):
            return self.tag('th', obj.components, obj.props)

        @self.handle(c.TableRow)
        def handle_tr(self, obj):
            return self.tag('tr', obj.components, obj.props)

        @self.handle(c.TableData)
        def handle_td(self, obj):
            return self.tag('td', obj.components, obj.props)
