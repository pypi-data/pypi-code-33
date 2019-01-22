import cgi

from docify import Document, components as c
from docify.lib.formatter import Formatter


DOC_TMPL = '''\
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <title>Docify Document</title>
    </head>
    <body>
        <div>
{}
            <footer>
                <p>&nbsp;</p>
                <small>
                    <cite>
                        This document generated using
                        <a href="https://github.com/rapidstack/docify">
                            Docify
                        </a>
                    </cite>
                </small>
            </footer>
        </div>
    </body>
</html>
'''


class HTML(Formatter):
    handlers = {
        Document: lambda x: DOC_TMPL.format(
            '\n'.join(map(lambda y: HTML.f(c.Div(y)), x.components))),

        c.Nbsp: lambda x: '&nbsp;',

        c.Li: lambda x: '{0}<li>\n{1}\n{0}</li>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.A: lambda x: '{0}<a href="{1}">\n{2}\n{0}</a>'.format(
            HTML.i(x.depth), x.href.replace('"', '\\"'), HTML.f(x.element)),

        c.Div: lambda x: '{0}<div>\n{1}\n{0}</div>'.format(
            HTML.i(x.depth), '\n'.join(map(HTML.f, x.children))),

        c.Ol: lambda x: '{0}<ol>\n{1}\n{0}</ol>'.format(
            HTML.i(x.depth), '\n'.join(map(HTML.f, x.children))),

        c.Ul: lambda x: '{0}<ul>\n{1}\n{0}</ul>'.format(
            HTML.i(x.depth), '\n'.join(map(HTML.f, x.children))),

        c.H1: lambda x: '{0}<h1>\n{1}\n{0}</h1>{2}'.format(
            HTML.i(x.depth), HTML.f(x.element), HTML.f(c.Hr())),

        c.H2: lambda x: '{0}<h2>\n{1}\n{0}</h2>{2}'.format(
            HTML.i(x.depth), HTML.f(x.element), HTML.f(c.Hr())),

        c.H3: lambda x: '{0}<h3>\n{1}\n{0}</h3>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.H4: lambda x: '{0}<h4>\n{1}\n{0}</h4>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.H5: lambda x: '{0}<h5>\n{1}\n{0}</h5>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.H6: lambda x: '{0}<h6>\n{1}\n{0}</h6>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.I: lambda x: '{0}<i>\n{1}\n{0}</i>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.B: lambda x: '{0}<b>\n{1}\n{0}</b>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.Br: lambda x: '{0}<br />'.format(HTML.i(x.depth)),

        c.Hr: lambda x: '{0}<hr />'.format(HTML.i(x.depth)),

        c.Code: lambda x: '{0}<code>{1}</code>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.Pre: lambda x: '{0}<pre>{1}</pre>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.Blockquote: lambda x: '{0}<blockquote>\n{1}\n{0}</blockquote>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.Del: lambda x: '{0}<del>\n{1}\n{0}</del>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.Span: lambda x: '{0}<span>\n{1}\n{0}</span>'.format(
            HTML.i(x.depth), HTML.f(x.element)),

        c.Img: lambda x: '{0}<img src="{1}" alt="{2}" />'.format(
            HTML.i(x.depth), x.src.replace('"', '\\"'), x.alt.replace('"', '\\"'))
    }

    @classmethod
    def escape(cls, txt):
        '''Overriding escape method'''
        return cgi.escape(txt)

    @staticmethod
    def i(depth):
        return ' ' * (12 + (depth * 4))
