import re

from docify.lib.formatter import Formatter
from docify import Document, components as c


class Markdown(Formatter):
    '''Markdown formatter to format document into plain markdown.'''

    def __init__(self, *args, **kwargs):
        super(Markdown, self).__init__(*args, **kwargs)
        self.newline_types = set([
            c.Blockquote, c.Break, c.Footer, c.Header1,
            c.Header2, c.Header3, c.Header4, c.Header5,
            c.Header6, c.HorizontalRule, c.OrderedList, c.ListItem,
            c.Paragraph, c.Pre, c.Section, c.Table, c.UnorderedList
        ])

    def r(self, txt, component):
        '''Helps rendering a formatted string with required line gaps.

        :param str txt: Formatted string.
        :param Component component: Component to render.
        '''
        ctype = type(component)
        ntype = type(component.next)
        if ctype in self.newline_types:
            txt += '\n'
        elif ntype in self.newline_types:
            txt += '\n'
            # if ctype not in self.newline_types:
            #     txt += '\n'
        return txt

    def update_handlers(self):
        '''Overriding parent method'''

        super(Markdown, self).update_handlers()

        @self.handle(Document)
        def handle_doc(self, obj):
            return ''.join(map(lambda c: self.r(self.f(c), c), obj.components))

        @self.handle(c.Text)
        def handle_text(self, obj):
            return self.r(
                re.sub(r'((([_*]).+?\3[^_*]*)*)([_*])', r'\g<1>\\\\\g<4>', obj.value), obj)

        @self.handle(c.Nbsp)
        def handle_nbsp(self, obj):
            return self.r(' ', obj)

        @self.handle(c.Break)
        def handle_br(self, obj):
            return self.r('', obj)

        @self.handle(c.HorizontalRule)
        def handle_hr(self, obj):
            return self.r('--------------------', obj)

        @self.handle(c.Anchor)
        def handle_a(self, obj):
            return self.r('[{}]({})'.format(self.f(obj.value), obj.props['href']), obj)

        @self.handle(c.Image)
        def handle_img(self, obj):
            return self.r('![{}]({})'.format(obj.props['alt'], obj.props['src']), obj)

        @self.handle(
            c.Footer, c.Small, c.Section, c.Paragraph, c.Span,
            c.ListItem, c.TableData, c.Table)
        def handle_default(self, obj):
            return self.r(''.join(map(
                lambda c: self.r(self.f(c), c), obj.components)), obj)

        @self.handle(c.Header1)
        def handle_h1(self, obj):
            return self.r('{}\n==============='.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Header2)
        def handle_h2(self, obj):
            return self.r('{}\n---------------'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Header3)
        def handle_h3(self, obj):
            return self.r('### {}'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Header4)
        def handle_h4(self, obj):
            return self.r('#### {}'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Header5)
        def handle_h5(self, obj):
            return self.r('##### {}'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Header6)
        def handle_h6(self, obj):
            return self.r('###### {}'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Cite, c.Italic)
        def handle_cite_i(self, obj):
            return self.r('*{}*'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Bold, c.TableHeader)
        def handle_b(self, obj):
            return self.r('**{}**'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Blockquote)
        def handle_blockquote(self, obj):
            return self.r('> {}'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Pre)
        def handle_pre(self, obj):
            return self.r('```\n{}\n```'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.Code)
        def handle_code(self, obj):
            if type(obj.parent) != c.Pre:
                return self.r('``{}``'.format(
                    ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
                ), obj)
            return self.r(''.join(map(
                lambda c: self.r(self.f(c), c), obj.components)), obj)

        @self.handle(c.Del)
        def handle_del(self, obj):
            return self.r('~~{}~~'.format(
                ''.join(map(lambda c: self.r(self.f(c), c), obj.components)),
            ), obj)

        @self.handle(c.OrderedList)
        def handle_ol(self, obj):
            txt = ''
            n, d = 0, 0
            p = obj.parent
            while isinstance(p, c._List):
                d += 1
                p = p.parent

            for x in obj.components:
                n += 1
                if isinstance(x, c._List):
                    txt += self.r(self.f(x), x)
                    continue
                txt += self.r('{}{}. {}'.format(
                    ' ' * d * 3, n, self.f(x)), x)
            return self.r(txt, obj)

        @self.handle(c.UnorderedList)
        def handle_ul(self, obj):
            txt = ''
            d = 0
            p = obj.parent
            while isinstance(p, c._List):
                d += 1
                p = p.parent
            for x in obj.components:
                if isinstance(x, c._List):
                    txt += self.r(self.f(x), x)
                    continue
                txt += self.r('{}* {}'.format(
                    ' ' * d * 3, self.f(x)), x)
            return self.r(txt, obj)

        @self.handle(c.TableRow)
        def handle_tr(self, obj):
            txt = ' | '.join(map(self.f, obj.components))
            txt += '\n'
            if obj.prev is None:
                txt += ' | '.join(['-' * 10] * len(obj.components))
                txt += '\n'
            return self.r(txt, obj)
