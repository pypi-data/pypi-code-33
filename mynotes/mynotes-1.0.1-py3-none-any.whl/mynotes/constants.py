"""Constant and default values."""

# mynotes builds indexes and converts to HTML a tree of notes written in
# Markdown.
# Copyright (C) 2018 Yorick Brunet <mynotes@yok.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re

VERSION = '1.0.1'
"""Version number."""

PACKAGE_NAME = 'mynotes'
"""Package name."""

CONFIG_FILE = '.' + PACKAGE_NAME + '.ini'
"""Configuration file."""

MARKDOWN_EXT = '.md'
"""Markdown extension to be considered."""

HTML_EXT = '.html'
"""HTML extension."""

INDEX_FILE = 'index' + MARKDOWN_EXT
"""Index file of a directory."""

HOME_FILE = 'home' + MARKDOWN_EXT
"""Main file of a directory."""

HTML_DIR = '_html'
"""Directory containing the generated html files."""

EXTRA_FILES_DIR = '_files'
"""Directory containing non-notes files, but with extra info."""

# TODO ADD JUPYTER_NOTEBOOK_DIR ?

EXCLUDE_DIRS = ['.git',
                EXTRA_FILES_DIR,
                HTML_DIR,
                ]
"""Excluded directories.

* .git : Git directory
* :ref:`EXTRA_FILES_DIR` : Non-notes directory for storing additional data in
notes tree
* :ref:`HTML_DIR` : Directory containing the generated html files
"""

EXCLUDE_FILES = ['.gitignore',
                 '.python-version',
                 'Makefile',
                 INDEX_FILE,
                 CONFIG_FILE,
                 ]
"""Excluded files.

* .gitignore : Git ignore file
* .python-version : pyenv settings
* Makefile : Local Makefile
* :ref:`INDEX_FILE` : Default index file
* :ref:`CONFIG_FILE` : Default configuration file
"""

RE_HEADER = re.compile(r'^# ([A-Za-zàéüä0-9\_\-\.\(\) ]+)')
"""Regular expression parser for extracting Markdown file title.

Title must be on one line and formatted as follows:
# TITLE
"""

RE_ANCHOR = re.compile(r'^((#+) ([A-Za-zàéüä0-9\_\-\.\(\) ]+))', re.MULTILINE)
"""Regular expression parser for extracting HTML file headers."""

HTML_HEADER = '''<!DOCTYPE html>
                 <html>
                   <head>
                       <meta charset="utf-8">
                       <title>{:s}</title>
                       <style type="text/css">{:s}</style>
                   </head>
                   <body>'''
"""HTML header for HTML files."""

HTML_FOOTER = '''</body></html>'''
"""HTML footer for HTML files."""

GFM_CSS = '''
.highlight { background-color: #f0f0f0 }
table { border-collapse: collapse; }
table, th, td { border: 1px solid black; }
tr:hover {background-color: #f5f5f5;}
blockquote { margin: 1.5em 0px; font-size: inherit;
             color: rgb(124, 135, 156);
             border-color: rgb(75, 83, 98); border-width: 4px;
             margin-left: 30px; padding: 0px 15px;
             color: rgb(119, 119, 119);
             border-left: 4px solid rgb(221, 221, 221);}
'''
"""Extra CSS styles for py-gfm parser.

Used in addition to Pygments HtmlFormatter styles.
"""

PLUGIN_HTML_LINKS_INDEX = 'links-index'
"""HTML Plugin: Insert links to upper/top index at top of each HTML file."""

PLUGIN_HTML_TOC = 'toc'
"""HTML Plugin: Insert ToC at top of each HTML file."""

PLUGINS_HTML = [PLUGIN_HTML_LINKS_INDEX,
                PLUGIN_HTML_TOC,
                ]
"""Available HTML plugins that can be activated."""

# autoapi.sphinx directive
__api__ = [
    'VERSION',
    'PACKAGE_NAME',
    'CONFIG_FILE',
    'MARKDOWN_EXT'
    'INDEX_FILE',
    'HOME_FILE',
    'HTML_DIR',
    'EXTRA_FILES_DIR',
    'EXCLUDE_DIRS',
    'EXCLUDE_FILES',
    'RE_HEADER',
    'RE_ANCHOR',
    'HTML_HEADER',
    'HTML_FOOTER',
    'GFM_CSS',
    'PLUGIN_HTML_LINKS_INDEX',
    'PLUGIN_HTML_TOC',
    'PLUGINS_HTML',
]
