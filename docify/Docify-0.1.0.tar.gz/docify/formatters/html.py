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
<a href="https://github.com/rapidstack/docify">Docify</a>
</cite>
</small>
</footer>
</div>
</body>
</html>
'''


class HTML(Formatter):
    '''HTML fomatter to format `Document`'''

    @classmethod
    def handlers(cls):
        '''Get the component handlers'''

        return {
            str: cgi.escape,

            Document: lambda x: DOC_TMPL.format(
                '\n'.join(map(cls.f, x.components))),

            c.Nbsp: lambda x: '&nbsp;',

            c.Li: lambda x: '<li>{}</li>'.format(cls.f(x.element)),

            c.A: lambda x: '<a href="{}">{}</a>'.format(
                x.href.replace('"', '\\"'), cls.f(x.element)),

            c.P: lambda x: '<p>\n{}\n</p>'.format(
                '\n'.join(map(cls.f, x.children))),

            c.Ol: lambda x: '<ol>\n{}\n</ol>'.format(
                '\n'.join(map(cls.f, x.children))),

            c.Ul: lambda x: '<ul>\n{}\n</ul>'.format(
                '\n'.join(map(cls.f, x.children))),

            c.H1: lambda x: '<h1>{}</h1>'.format(cls.f(x.element)),

            c.H2: lambda x: '<h2>{}</h2>'.format(cls.f(x.element)),

            c.H3: lambda x: '<h3>{}</h3>'.format(cls.f(x.element)),

            c.H4: lambda x: '<h4>{}</h4>'.format(cls.f(x.element)),

            c.H5: lambda x: '<h5>{}</h5>'.format(cls.f(x.element)),

            c.H6: lambda x: '<h6>{}</h6>'.format(cls.f(x.element)),

            c.I: lambda x: '<i>{}</i>'.format(cls.f(x.element)),

            c.B: lambda x: '<b>{}</b>'.format(cls.f(x.element)),

            c.Br: lambda x: '<br />'.format(cls.i(x.depth)),

            c.Hr: lambda x: '<hr />'.format(cls.i(x.depth)),

            c.Code: lambda x: '<code>{}</code>'.format(cls.f(x.element)),

            c.Pre: lambda x: '<pre>{}</pre>'.format(cls.f(x.element)),

            c.Blockquote: lambda x: '<blockquote>{}</blockquote>'.format(
                cls.f(x.element)),

            c.Del: lambda x: '<del>{}</del>'.format(cls.f(x.element)),

            c.Span: lambda x: '<span>{}</span>'.format(
                ''.join(map(cls.f, x.children))),

            c.Img: lambda x: '<img src="{}" alt="{}" />'.format(
                x.src.replace('"', '\\"'), x.alt.replace('"', '\\"'))
        }

    @staticmethod
    def i(depth):
        '''Create indentation based on depth.

        :param int depth: Depth of object.
        '''
        return ' ' * (8 + (depth * 4))
