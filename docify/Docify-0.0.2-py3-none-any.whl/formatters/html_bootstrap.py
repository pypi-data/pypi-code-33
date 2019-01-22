import cgi

from docify import Document, components as c
from docify.lib.formatter import Formatter


DOC_TMPL = '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

        <title>Docify Document</title>
    </head>
    <body>
        <div class="sidebar col-md-3"></div>
        <div class="container col-md-6">
{}
            <footer>
                <p>&nbsp;</p>
                <small>
                    <cite>
                        This document is generated using
                        <a href="https://github.com/rapidstack/docify">
                            Docify
                        </a>
                    </cite>
                </small>
            </footer>
        </div>
        <div class="sidebar col-md-3"></div>
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    </body>
</html>
'''


class HTMLBootstrap(Formatter):
    handlers = {
        Document: lambda x: DOC_TMPL.format('\n'.join(
            map(lambda y: HTMLBootstrap.f(c.Div(y)), x.components))),

        c.Nbsp: lambda x: '&nbsp;',

        c.Li: lambda x: '{0}<li>\n{1}\n{0}</li>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.A: lambda x: '{0}<a href="{1}">\n{2}\n{0}</a>'.format(
            HTMLBootstrap.i(x.depth), x.href.replace('"', '\\"'),
            HTMLBootstrap.f(x.element)),

        c.Div: lambda x: ('{0}<div class="row"><div class="col-md-12">'
                          '\n{1}\n{0}</div></div>').format(
            HTMLBootstrap.i(x.depth),
            '\n'.join(map(HTMLBootstrap.f, x.children))),

        c.Ol: lambda x: '{0}<ol>\n{1}\n{0}</ol>'.format(
            HTMLBootstrap.i(x.depth), '\n'.join(map(
                HTMLBootstrap.f, x.children))),

        c.Ul: lambda x: '{0}<ul>\n{1}\n{0}</ul>'.format(
            HTMLBootstrap.i(x.depth), '\n'.join(map(
                HTMLBootstrap.f, x.children))),

        c.H1: lambda x: '{0}<h1>\n{1}\n{0}</h1>{2}'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element),
            HTMLBootstrap.f(c.Hr())),

        c.H2: lambda x: '{0}<h2>\n{1}\n{0}</h2>{2}'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element),
            HTMLBootstrap.f(c.Hr())),

        c.H3: lambda x: '{0}<h3>\n{1}\n{0}</h3>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.H4: lambda x: '{0}<h4>\n{1}\n{0}</h4>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.H5: lambda x: '{0}<h5>\n{1}\n{0}</h5>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.H6: lambda x: '{0}<h6>\n{1}\n{0}</h6>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.I: lambda x: '{0}<i>\n{1}\n{0}</i>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.B: lambda x: '{0}<b>\n{1}\n{0}</b>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.Br: lambda x: '{0}<br />'.format(HTMLBootstrap.i(x.depth)),

        c.Hr: lambda x: '{0}<hr />'.format(HTMLBootstrap.i(x.depth)),

        c.Code: lambda x: '{0}<code class="bg-light rounded p-1">{1}</code>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.Pre: lambda x: '{0}<pre class="bg-light rounded p-3">{1}</pre>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.Blockquote: lambda x: ('{0}<blockquote>'
                                 '\n{1}\n{0}</blockquote>').format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.Del: lambda x: '{0}<del>\n{1}\n{0}</del>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.Span: lambda x: '{0}<span>\n{1}\n{0}</span>'.format(
            HTMLBootstrap.i(x.depth), HTMLBootstrap.f(x.element)),

        c.Img: lambda x: '{0}<img src="{1}" alt="{2}" />'.format(
            HTMLBootstrap.i(x.depth), x.src.replace('"', '\\"'),
            x.alt.replace('"', '\\"'))
    }

    @classmethod
    def escape(cls, txt):
        '''Overriding escape method'''
        return cgi.escape(txt)

    @staticmethod
    def i(depth):
        return ' ' * (12 + (depth * 4))
