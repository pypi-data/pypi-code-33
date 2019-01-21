# -*- coding: utf-8 -*-
"""
    werkzeug.debug.util
    ~~~~~~~~~~~~~~~~~~~

    Utilities for the debugger.

    :copyright: 2007 by Georg Brandl, Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import os
import re
import sys
import token
import inspect
import keyword
import tokenize
import traceback
from cgi import escape
from werkzeug.local import Local
from six import BytesIO, StringIO
import six

local = Local()
inspect.getsourcefile = inspect.getfile

class HTMLStringO(object):
    """A StringO version that HTML escapes on write."""

    def __init__(self):
        self._buffer = []

    def isatty(self):
        return False

    def close(self):
        pass

    def flush(self):
        pass

    def seek(self, n, mode=0):
        pass

    def readline(self):
        if len(self._buffer) == 0:
            return ''
        ret = self._buffer[0]
        del self._buffer[0]
        return ret

    def reset(self):
        val = ''.join(self._buffer)
        del self._buffer[:]
        return val

    def _write(self, x):
        if isinstance(x, bytes):
            x = x.decode('utf-8', 'replace')
        self._buffer.append(x)

    def write(self, x):
        self._write(x)

    def writelines(self, x):
        self._write(''.join(x))

class ExceptionRepr(object):

    def __init__(self, exc):
        exclines = traceback.format_exception_only(type(exc), exc)
        self.repr = 'got %s' % exclines[-1].strip()

    def __repr__(self):
        return self.repr


class Namespace(object):

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def to_dict(self):
        return self.__dict__.copy()


class ThreadedStream(object):
    """
    Thin wrapper around sys.stdout so that we can dispatch access
    to it for different threads.
    """

    def push():
        if not isinstance(sys.stdout, ThreadedStream):
            sys.stdout = ThreadedStream()
        local.stream = HTMLStringO()
    push = staticmethod(push)

    def fetch():
        try:
            stream = local.stream
        except AttributeError:
            return ''
        return stream.reset()
    fetch = staticmethod(fetch)

    def install(cls):
        sys.stdout = cls()
    install = classmethod(install)

    def __setattr__(self, name, value):
        raise AttributeError('read only attribute %s' % name)

    def __getattribute__(self, name):
        if name == '__members__':
            return dir(sys.__stdout__)
        try:
            stream = local.stream
        except AttributeError:
            stream = sys.__stdout__
        return getattr(stream, name)

    def __repr__(self):
        return repr(sys.__stdout__)


def get_uid():
    """Return a random unique ID."""
    import uuid
    
    return uuid.uuid4().hex[:8]
#    
#    return str(random()).encode('base64')[3:11]


def highlight_python(source):
    """Highlight some python code. Return a list of lines"""
    parser = PythonParser(source)
    parser.parse()
    return parser.get_html_output()


class PythonParser(object):
    """
    Simple python sourcecode highlighter.

    Usage::

        p = PythonParser(source)
        p.parse()
        for line in p.get_html_output():
            print line
    """

    _KEYWORD = token.NT_OFFSET + 1
    _TEXT    = token.NT_OFFSET + 2
    _classes = {
        token.NUMBER:       'num',
        token.OP:           'op',
        token.STRING:       'str',
        tokenize.COMMENT:   'cmt',
        token.NAME:         'id',
        token.ERRORTOKEN:   'error',
        _KEYWORD:           'kw',
        _TEXT:              'txt',
    }

    def __init__(self, raw):
        self.raw = raw.expandtabs(8)
#        if isinstance(self.raw, six.text_type):
#            self.raw = self.raw.encode('utf-8', 'ignore')
        self.out = StringIO()
        self.encoding = 'utf8'

    def parse(self):
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find(b'\n', pos) + 1
            if not pos:
                break
            self.lines.append(pos)
        self.lines.append(len(self.raw))

        self.pos = 0
        text = BytesIO(self.raw)
        try:
            for v in tokenize.generate_tokens(text.readline):
                if six.PY3:
                    if v[0] is tokenize.ENCODING:
                        self.encoding = v[1]
                        continue
                self(*v)
        except (SyntaxError, tokenize.TokenError):
            self.error = True
        else:
            self.error = False

    def get_html_output(self):
        """ Return line generator. """
        def html_splitlines(lines):
            # this cool function was taken from trac.
            # http://projects.edgewall.com/trac/
            open_tag_re = re.compile(r'<(\w+)(\s.*)?[^/]?>')
            close_tag_re = re.compile(r'</(\w+)>')
            open_tags = []
            for line in lines:
                for tag in open_tags:
                    line = tag.group(0) + line
                open_tags = []
                for tag in open_tag_re.finditer(line):
                    open_tags.append(tag)
                open_tags.reverse()
                for ctag in close_tag_re.finditer(line):
                    for otag in open_tags:
                        if otag.group(1) == ctag.group(1):
                            open_tags.remove(otag)
                            break
                for tag in open_tags:
                    line += '</%s>' % tag.group(1)
                yield line

        if self.error:
            return escape(self.raw).splitlines()
        return list(html_splitlines(self.out.getvalue().splitlines()))

    def __call__(self, toktype, toktext, s_row_col, e_row_col, line):
        (srow,scol) = s_row_col
        (erow,ecol) = e_row_col
        oldpos = self.pos
        newpos = scol
        self.pos = ecol

        if toktype in [token.NEWLINE, tokenize.NL]:
            self.out.write('\n')
            self.pos = 0
            return

        if newpos > oldpos:
            self.out.write(line[oldpos:newpos])
        
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return

        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = self._KEYWORD
        clsname = self._classes.get(toktype, 'txt')

        self.out.write('<span class="code-item p-%s">%s</span>' % (
            clsname,
            escape(toktext)
        ))


def get_frame_info(tb, context_lines=7, simple=False):
    """
    Return a dict of information about a given traceback.
    """
    # line numbers / function / variables
    lineno = tb.tb_lineno
    function = tb.tb_frame.f_code.co_name
    variables = tb.tb_frame.f_locals

    # get filename
    if simple:
        fn = tb.tb_frame.f_code.co_filename
    else:
        fn = tb.tb_frame.f_globals.get('__file__')
        if not fn:
            fn = os.path.realpath(inspect.getsourcefile(tb) or
                                  inspect.getfile(tb))
        if fn[-4:] in ('.pyc', '.pyo'):
            fn = fn[:-1]

    # module name
    modname = tb.tb_frame.f_globals.get('__name__')

    # get loader
    loader = tb.tb_frame.f_globals.get('__loader__')
    if not loader:
        loader = tb.tb_frame.f_locals.get('__loader__')
        
        b = tb.tb_frame
        while not loader:
            b = b.f_back
            if not b:
                break
            loader = b.f_locals.get('__loader__')

    exc_type, exc_value, exc_info = sys.exc_info()
    
    # sourcecode
    source = ''
    pre_context, post_context = [], []
    context_line = raw_context_line = context_lineno = None
    try:
        if not loader is None and hasattr(loader, 'test') and loader.test(fn):
            source = ''
            if hasattr(loader, 'get_source'):
                fn, lineno, source = loader.get_source(exc_type, exc_value, exc_info, tb)
        else:
            source = open(fn, 'rb').read()
            
    except:
        pass
    else:
        try:
            raw_context_line = source.splitlines()[lineno - 1].strip().decode('utf8')
        except IndexError:
            pass
        if not simple:
            parsed_source = highlight_python(source)
            lbound = max(0, lineno - context_lines - 1)
            ubound = lineno + context_lines
            try:
                context_line = parsed_source[lineno - 1]
                pre_context = parsed_source[lbound:lineno - 1]
                post_context = parsed_source[lineno:ubound]
            except IndexError as e:
                pass
            context_lineno = lbound

    if isinstance(fn, six.text_type):
        fn = fn.encode('utf-8')
    return {
        'tb':               tb,
        'filename':         fn,
        'basename':         os.path.basename(fn),
        'loader':           loader,
        'function':         function,
        'lineno':           lineno,
        'vars':             variables,
        'pre_context':      pre_context,
        'context_line':     context_line,
        'raw_context_line': raw_context_line,
        'post_context':     post_context,
        'context_lineno':   context_lineno,
        'source':           source
    }
