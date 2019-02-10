# coding: utf-8


"""
    python-creole
    ~~~~~~~~~~~~~

    :homepage:
      http://code.google.com/p/python-creole/
    
    :sourcecode:
      http://github.com/jedie/python-creole
    
    :PyPi:
      http://pypi.python.org/pypi/python-creole/

    :copyleft: 2008-2014 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import division, absolute_import, print_function, unicode_literals

__version__ = (1, 2, 1)
__api__ = (1, 0) # Creole 1.0 spec - http://wikicreole.org/


import os
import sys
import warnings

from mycms.creole.creole2html.emitter import HtmlEmitter
from mycms.creole.creole2html.parser import BlockRules, CreoleParser
from mycms.creole.html_parser.parser import HtmlParser
from mycms.creole.py3compat import TEXT_TYPE


# TODO: Add git date to __version__


VERSION_STRING = '.'.join(str(part) for part in __version__)
API_STRING = '.'.join(str(integer) for integer in __api__)


def creole2html(markup_string, debug=False,
        parser_kwargs={}, emitter_kwargs={},
        block_rules=None, blog_line_breaks=True,
        macros=None, verbose=None, stderr=None,
        view=None,
    ):
    """
    convert creole markup into html code

    >>> creole2html('This is **creole //markup//**!')
    '<p>This is <strong>creole <i>markup</i></strong>!</p>'
    
    Info: parser_kwargs and emitter_kwargs are deprecated
    """
    assert isinstance(markup_string, TEXT_TYPE), "given markup_string must be unicode!"

    parser_kwargs2 = {
        "block_rules": block_rules,
        "blog_line_breaks": blog_line_breaks,
    }
    if parser_kwargs:
        warnings.warn("parser_kwargs argument in creole2html would be removed in the future!", PendingDeprecationWarning)
        parser_kwargs2.update(parser_kwargs)

    # Create document tree from mycms.creole markup
    document = CreoleParser(markup_string, **parser_kwargs2).parse()
    if debug:
        document.debug()

    emitter_kwargs2 = {
        "macros": macros,
        "verbose": verbose,
        "stderr": stderr,
        "view":view,
    }
    if emitter_kwargs:
        warnings.warn("emitter_kwargs argument in creole2html would be removed in the future!", PendingDeprecationWarning)
        emitter_kwargs2.update(emitter_kwargs)

    # Build html code from document tree
    return HtmlEmitter(document, **emitter_kwargs2).emit()


def parse_html(html_string, debug=False):
    """ create the document tree from html code """
    assert isinstance(html_string, TEXT_TYPE), "given html_string must be unicode!"

    h2c = HtmlParser(debug=debug)
    document_tree = h2c.feed(html_string)
    if debug:
        h2c.debug()
    return document_tree





if __name__ == '__main__':
    print("runing local doctest...")
    import doctest
    print(doctest.testmod(
#            verbose=True
    ))
