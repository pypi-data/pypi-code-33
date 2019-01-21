#! /usr/bin/env python
# coding=utf-8
# Originally written by Barry Warsaw <barry@zope.com>
#
# Minimally patched to make it even more xgettext compatible
# by Peter Funk <pf@artcom-gmbh.de>
#
# 2002-11-22 J?gen Hermann <jh@web.de>
# Added checks that _() only contains string literals, and
# command line args are resolved to module lists, i.e. you
# can now pass a filename, a module or package name, or a
# directory (including globbing chars, important for Win32).
# Made docstring fit in 80 chars wide displays using pydoc.
# 
# 2010-06-12 Jan-Hendrik G?lner <jan-hendrik.goellner@gmx.de>
# Made it plural sensitive, added ngettext as default keyword.
# Any keyworded function that is being supplied > 2 arguments
# is treated like ngettext.
# Also added support for constructs like "_('foo' + 10*'bar')"
# by evaluating the whole expression.
# Code like _(foo(arg1, arg2) + "bar") does not work by design
# as that expression must be evaluated at runtime and this script
# only extracts static strings known before runtime.
# However it is possible to do things like
#   "ngettext('World', 'Worlds', numWorlds)"
# as only the first two arguments are evaluated.
# Advanced version number from 1.5 to 1.6
#
from __future__ import print_function, absolute_import, unicode_literals
# for selftesting
import sys
sys.path.insert(0, '..')
try:
    import fintl
    _ = fintl.gettext
except ImportError:
    _ = lambda s: s
from uliweb.utils.common import walk_dirs
from ..utils._compat import text_type, b, u

__doc__ = """pygettext -- Python equivalent of xgettext(1)

Many systems (Solaris, Linux, Gnu) provide extensive tools that ease the
internationalization of C programs. Most of these tools are independent of
the programming language and can be used from within Python programs.
Martin von Loewis' work[1] helps considerably in this regard.

There's one problem though; xgettext is the program that scans source code
looking for message strings, but it groks only C (or C++). Python
introduces a few wrinkles, such as dual quoting characters, triple quoted
strings, and raw strings. xgettext understands none of this.

Enter pygettext, which uses Python's standard tokenize module to scan
Python source code, generating .pot files identical to what GNU xgettext[2]
generates for C and C++ code. From there, the standard GNU tools can be
used.

A word about marking Python strings as candidates for translation. GNU
xgettext recognizes the following keywords: gettext, dgettext, dcgettext,
and gettext_noop. But those can be a lot of text to include all over your
code. C and C++ have a trick: they use the C preprocessor. Most
internationalized C source includes a #define for gettext() to _() so that
what has to be written in the source is much less. Thus these are both
translatable strings:

    gettext("Translatable String")
    _("Translatable String")

Python of course has no preprocessor so this doesn't work so well.  Thus,
pygettext searches only for _() by default, but see the -k/--keyword flag
below for how to augment this.

 [1] http://www.python.org/workshops/1997-10/proceedings/loewis.html
 [2] http://www.gnu.org/software/gettext/gettext.html

NOTE: pygettext attempts to be option and feature compatible with GNU
xgettext where ever possible. However some options are still missing or are
not fully implemented. Also, xgettext's use of command line switches with
option arguments is broken, and in these cases, pygettext just defines
additional switches.

Usage: pygettext [options] inputfile ...

Options:

    -a
    --extract-all
        Extract all strings.

    -d name
    --default-domain=name
        Rename the default output file from messages.pot to name.pot.

    -E
    --escape
        Replace non-ASCII characters with octal escape sequences.

    -D
    --docstrings
        Extract module, class, method, and function docstrings.  These do
        not need to be wrapped in _() markers, and in fact cannot be for
        Python to consider them docstrings. (See also the -X option).

    -h
    --help
        Print this help message and exit.

    -k word
    --keyword=word
        Keywords to look for in addition to the default set, which are:
        %(DEFAULTKEYWORDS)s

        You can have multiple -k flags on the command line.

    -K
    --no-default-keywords
        Disable the default set of keywords (see above).  Any keywords
        explicitly added with the -k/--keyword option are still recognized.

    --no-location
        Do not write filename/lineno location comments.

    -n
    --add-location
        Write filename/lineno location comments indicating where each
        extracted string is found in the source.  These lines appear before
        each msgid.  The style of comments is controlled by the -S/--style
        option.  This is the default.

    -o filename
    --output=filename
        Rename the default output file from messages.pot to filename.  If
        filename is `-' then the output is sent to standard out.

    -p dir
    --output-dir=dir
        Output files will be placed in directory dir.

    -S stylename
    --style stylename
        Specify which style to use for location comments.  Two styles are
        supported:

        Solaris  # File: filename, line: line-number
        GNU      #: filename:line

        The style name is case insensitive.  GNU style is the default.

    -v
    --verbose
        Print the names of the files being processed.

    -V
    --version
        Print the version of pygettext and exit.

    -w columns
    --width=columns
        Set width of output to columns.

    -x filename
    --exclude-file=filename
        Specify a file that contains a list of strings that are not be
        extracted from the input files.  Each string to be excluded must
        appear on a line by itself in the file.

    -X filename
    --no-docstrings=filename
        Specify a file that contains a list of files (one per line) that
        should not have their docstrings extracted.  This is only useful in
        conjunction with the -D option above.

If `inputfile' is -, standard input is read.
"""

import os
import imp
import sys
import glob
import time
import getopt
import token
import tokenize

__version__ = '1.6'

default_keywords = ['_', 'ngettext']
DEFAULTKEYWORDS = ', '.join(default_keywords)

EMPTYSTRING = ''


# The normal pot-file header. msgmerge and Emacs's po-mode work better if it's
# there.
pot_header = '''\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# {First_Author}, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: {Project_Id_Version}\\n"
"POT-Creation-Date: {time}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: {Last_Translator}\\n"
"Language-Team: {Language_Team}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset={Content_Type_Charset}\\n"
"Content-Transfer-Encoding: {Content_Transfer_Encoding}\\n"
"Plural-Forms: {Plural_Forms}\\n"
"Generated-By: pygettext.py {version}\\n"

'''

def usage(code, msg=''):
    print(__doc__ % globals(), file=sys.stderr)
    if msg:
        print(msg, file=sys.stderr)
    sys.exit(code)


escapes = []

def make_escapes(pass_iso8859):
    global escapes
#    if pass_iso8859:
#        # Allow iso-8859 characters to pass through so that e.g. 'msgid
#        # "H?e"' would result not result in 'msgid "H\366he"'.  Otherwise we
#        # escape any character outside the 32..126 range.
#        mod = 128
#    else:
#        mod = 256
#    for i in range(256):
#        if 32 <= (i % mod) <= 126:
#            escapes.append(chr(i))
#        else:
#            escapes.append("\\%03o" % i)
#    escapes[ord('\\')] = '\\\\'
#    escapes[ord('\t')] = '\\t'
#    escapes[ord('\r')] = '\\r'
#    escapes[ord('\n')] = '\\n'
#    escapes[ord('\"')] = '\\"'

__escapes__ = {}
__escapes__['\\'] = '\\\\'
__escapes__['\t'] = '\\t'
__escapes__['\r'] = '\\r'
__escapes__['\n'] = '\\n'
__escapes__['\"'] = '\\"'

def escape(s):
#    global escapes
    s = u(s)
    r = []
    for c in s:
        r.append(__escapes__.get(c, c))
    return EMPTYSTRING.join(r)


def safe_eval(s):
    # unwrap quotes, safely
    return eval(s, {'__builtins__':{}}, {})


def normalize(s):
    # This converts the various Python string types into a format that is
    # appropriate for .po files, namely much closer to C style.
    lines = s.split('\n')
    if len(lines) == 1:
        s = '"' + escape(s) + '"'
    else:
        if not lines[-1]:
            del lines[-1]
            lines[-1] = lines[-1] + '\n'
        for i in range(len(lines)):
            lines[i] = escape(lines[i])
        lineterm = '\\n"\n"'
        s = '""\n"' + lineterm.join(lines) + '"'
    return s

def containsAny(str, set):
    """Check whether 'str' contains ANY of the chars in 'set'"""
    return 1 in [c in str for c in set]


def _visit_pyfiles(list, dirname, names):
    """Helper for getFilesForName()."""
    # get extension for python source files
    if not globals().has_key('_py_ext'):
        global _py_ext
#        _py_ext = [triple[0] for triple in imp.get_suffixes()
#                   if triple[2] == imp.PY_SOURCE][0]
        _py_ext = [triple[0] for triple in imp.get_suffixes()
                   if triple[2] == imp.PY_SOURCE]
        
    # don't recurse into CVS directories
    if 'CVS' in names:
        names.remove('CVS')

    if '.svn' in names:
        names.remove('.svn')

    if '.git' in names:
        names.remove('.git')

    if 'static' in names:
        names.remove('static')
    
    # add all *.py files to list
    list.extend(
        [os.path.join(dirname, file) for file in names
         if os.path.splitext(file)[1] in _py_ext]
        )

def _get_modpkg_path(dotted_name, pathlist=None):
    """Get the filesystem path for a module or a package.

    Return the file system path to a file for a module, and to a directory for
    a package. Return None if the name is not found, or is a builtin or
    extension module.
    """
    # split off top-most name
    parts = dotted_name.split('.', 1)

    if len(parts) > 1:
        # we have a dotted path, import top-level package
        try:
            file, pathname, description = imp.find_module(parts[0], pathlist)
            if file: file.close()
        except ImportError:
            return None

        # check if it's indeed a package
        if description[2] == imp.PKG_DIRECTORY:
            # recursively handle the remaining name parts
            pathname = _get_modpkg_path(parts[1], [pathname])
        else:
            pathname = None
    else:
        # plain name
        try:
            file, pathname, description = imp.find_module(
                dotted_name, pathlist)
            if file:
                file.close()
            if description[2] not in [imp.PY_SOURCE, imp.PKG_DIRECTORY]:
                pathname = None
        except ImportError:
            pathname = None

    return pathname


def getFilesForName(name):
    """Get a list of module files for a filename, a module or package name,
    or a directory.
    """
    if not os.path.exists(name):
        # check for glob chars
        if containsAny(name, "*?[]"):
            files = glob.glob(name)
            alist = []
            for file in files:
                alist.extend(getFilesForName(file))
            return alist

        # try to find module or package
        name = _get_modpkg_path(name)
        if not name:
            return []

    if os.path.isdir(name):
        # find all python files in directory
        return list(walk_dirs(name, include_ext=['.py', '.ini', '.html'], file_only=True))
    elif os.path.exists(name):
        # a single file
        return [name]

    return []

class TokenEater:
    def __init__(self, options, vars=None):
        self.__options = options
        self.__messages = {}
        self.__state = self.__waiting
        self.__args = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = None
        self.__vars = vars

    def __call__(self, ttype, tstring, stup, etup, line):
        # dispatch
##        import token
##        print >> sys.stderr, 'ttype:', token.tok_name[ttype], \
##              'tstring:', tstring
        self.__state(ttype, tstring, stup[0])


    def __waiting(self, ttype, tstring, lineno):
        opts = self.__options
        # Do docstring extractions, if enabled
        if opts.docstrings and not opts.nodocstrings.get(self.__curfile):
            # module docstring?
            if self.__freshmodule:
                if ttype == tokenize.STRING:
                    try:
                        s = safe_eval(tstring)
                    except Exception as e:
                        print((
                            '*** %(file)s:%(lineno)s: could not evaluate argument "%(arg)s"'
                            ) % {
                            'arg': tstring,
                            'file': self.__curfile,
                            'lineno': self.__lineno
                            }, file=sys.stderr)
                        print(str(e), file=sys.stderr)
                    else:
                        self.__addentry([s], lineno, isdocstring=1)
                    self.__freshmodule = 0
                elif ttype not in (tokenize.COMMENT, tokenize.NL):
                    self.__freshmodule = 0
                return
            # class docstring?
            if ttype == tokenize.NAME and tstring in ('class', 'def'):
                self.__state = self.__suiteseen
                return
        if ttype == tokenize.NAME and tstring in opts.keywords:
            self.__state = self.__keywordseen

    def __suiteseen(self, ttype, tstring, lineno):
        # ignore anything until we see the colon
        if ttype == tokenize.OP and tstring == ':':
            self.__state = self.__suitedocstring

    def __suitedocstring(self, ttype, tstring, lineno):
        # ignore any intervening noise
        if ttype == tokenize.STRING:
            try:
                s = safe_eval(tstring)
            except Exception as e:
                print((
                    '*** %(file)s:%(lineno)s: could not evaluate argument "%(arg)s"'
                    ) % {
                    'arg': tstring,
                    'file': self.__curfile,
                    'lineno': self.__lineno
                    }, file=sys.stderr)
                print(str(e), file=sys.stderr)
            else:
                self.__addentry(s, lineno, isdocstring=1)
            self.__state = self.__waiting
        elif ttype not in (tokenize.NEWLINE, tokenize.INDENT,
                           tokenize.COMMENT):
            # there was no class docstring
            self.__state = self.__waiting

    def __keywordseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__args = ['']
            self.__lineno = lineno
            self.__depth = 0
            self.__state = self.__scanstring1
        else:
            self.__state = self.__waiting

    def __scanstring1(self, ttype, tstring, lineno):
        # handle first argument, which is supposed to be a string.
        if ttype == tokenize.OP and tstring == ')':
            # End of list of arguments for the current function call.
            # If the argument list is empty (as in keyword()), ignore this call.
            # otherwise evaluate the fragments we collected as the first
            # argument and record its line number and update the list of
            # messages seen. Reset state for the next batch.
            if self.__args[-1]:
                try:
                    s = safe_eval(self.__args[-1])
                except Exception as e:
                    print((
                        '*** %(file)s:%(lineno)s: could not evaluate argument "%(arg)s"'
                        ) % {
                        'arg': self.__args[-1],
                        'file': self.__curfile,
                        'lineno': self.__lineno
                        }, file=sys.stderr)
                    print(str(e), file=sys.stderr)
                    self.__state = self.__waiting
                    return
                if type(s) == str or type(s) == text_type:
                    self.__args[-1] = s
                    self.__addentry(self.__args)
                else:
                    print((
                        '*** %(file)s:%(lineno)s: argument is no str or unicode object "%(arg)s"'
                        ) % {
                        'arg': s,
                        'file': self.__curfile,
                        'lineno': self.__lineno
                        }, file=sys.stderr)
            self.__state = self.__waiting
        elif ttype == tokenize.OP and tstring == ',':
            # Start of the next argument.
            try:
                s = safe_eval(self.__args[-1])
            except Exception as e:
                print((
                    '*** %(file)s:%(lineno)s: could not evaluate argument "%(arg)s"'
                    ) % {
                    'arg': self.__args[-1],
                    'file': self.__curfile,
                    'lineno': self.__lineno
                    }, file=sys.stderr)
                print(str(e), file=sys.stderr)
                self.__state = self.__waiting
                return
            if type(s) == str or type(s) == text_type:
                self.__args[-1] = s
                self.__args.append('') # next argument.
                self.__state = self.__scanstring2
            else:
                print((
                    '*** %(file)s:%(lineno)s: argument 1 is no str or unicode object "%(arg)s"'
                    ) % {
                    'arg': s,
                    'file': self.__curfile,
                    'lineno': self.__lineno
                    }, file=sys.stderr)
                self.__state = self.__waiting
        else:
            # add string to current argument for later evaluation.
            # no state change in this case.
            self.__args[-1] += tstring

    def __scanstring2(self, ttype, tstring, lineno):
        # handle second argument, which is supposed to be a string.
        if ttype == tokenize.OP and tstring == ')':
            # End of list of arguments for the current function call.
            # This is an error if we expect either one or three arguments but
            # never two.
            print((
                '*** %(file)s:%(lineno)s: unexpected number of arguments (2)"'
                ) % {
                'file': self.__curfile,
                'lineno': self.__lineno
                }, file=sys.stderr)
            self.__state = self.__waiting
        elif ttype == tokenize.OP and tstring == ',':
            # Start of the next argument. We do not need to parse it, we only
            # made sure it is there and now we assume this is a plural call.
            try:
                s = safe_eval(self.__args[-1])
            except Exception as e:
                print((
                    '*** %(file)s:%(lineno)s: could not evaluate argument "%(arg)s"'
                    ) % {
                    'arg': self.__args[-1],
                    'file': self.__curfile,
                    'lineno': self.__lineno
                    }, file=sys.stderr)
                print(str(e), file=sys.stderr)
                self.__state = self.__waiting
                return
            s = safe_eval(self.__args[-1])
            if type(s) == str or type(s) == six.text_type:
                self.__args[-1] = s
                self.__addentry(self.__args)
                self.__state = self.__waiting
            else:
                print((
                    '*** %(file)s:%(lineno)s: argument 2 is no str or unicode object "%(arg)s"'
                    ) % {
                    'arg': s,
                    'file': self.__curfile,
                    'lineno': self.__lineno
                    }, file=sys.stderr)
                self.__state = self.__waiting
        else:
            # add string to current argument for later evaluation.
            # no state change in this case.
            self.__args[-1] += tstring

    def __addentry(self, args, lineno=None, isdocstring=0):
        isplural = 0
        if len(args) > 1:
            isplural = 1
        if lineno is None:
            lineno = self.__lineno
        exclude = 0
        if args[0] in self.__options.toexclude:
            exclude = 1
        if isplural:
            if args[1] not in self.__options.toexclude:
                # in case of plural, both strings must be in the toexclude list
                # to exclude this entry.
                exclude = 0
        if not exclude:
            entry = (self.__curfile, lineno)
            # entries look like this:
            # {('arg1','arg2') : {(filename,lineno) : <isdocstring>},
            #  ('arg1',)       : {(filename,lineno) : <iscodstring>}}
            # a key with len > 1 indicates plurals
            self.__messages.setdefault(tuple(args[0:2]), {})[entry] = isdocstring

    def set_filename(self, filename):
        self.__curfile = filename
        self.__freshmodule = 1

    def write(self, fp):
        options = self.__options
        timestamp = time.strftime('%Y-%m-%d %H:%M')
        # The time stamp in the header doesn't have the same format as that
        # generated by xgettext...
        d = self.__vars.copy()
        d.update({'time': timestamp, 'version': __version__})
        print(pot_header.format(**d), file=fp)
        # Sort the entries.  First sort each particular entry's keys, then
        # sort all the entries by their first item.
        reverse = {}
        for k, v in self.__messages.items():
            keys = sorted(v.keys())
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = reverse.keys()
        for rkey in sorted(rkeys):
            rentries = reverse[rkey]
            for k, v in sorted(rentries):
                # If the entry was gleaned out of a docstring, then add a
                # comment stating so.  This is to aid translators who may wish
                # to skip translating some unimportant docstrings.
                isdocstring = sum(v.values())
                # k is the message string, v is a dictionary-set of (filename,
                # lineno) tuples.  We want to sort the entries in v first by
                # file name and then by line number.
                v = sorted(v.keys())
                if not options.writelocations:
                    pass
                # location comments are different b/w Solaris and GNU:
                elif options.locationstyle == options.SOLARIS:
                    for filename, lineno in v:
                        d = {'filename': filename, 'lineno': lineno}
                        print((
                            '# File: %(filename)s, line: %(lineno)d') % d, file=fp)
                elif options.locationstyle == options.GNU:
                    # fit as many locations on one line, as long as the
                    # resulting line length doesn't exceeds 'options.width'
                    locline = '#:'
                    for filename, lineno in v:
                        d = {'filename': filename, 'lineno': lineno}
                        s = (' %(filename)s:%(lineno)d') % d
                        if len(locline) + len(s) <= options.width:
                            locline = locline + s
                        else:
                            print(locline, file=fp)
                            locline = "#:" + s
                    if len(locline) > 2:
                        print(locline, file=fp)
                if isdocstring:
                    print('#, docstring', file=fp)
                print('msgid', normalize(k[0]), file=fp)
                if len(k) > 1:
                    print('msgid_plural', normalize(k[1]), file=fp)
                    print('msgstr[0] ""', file=fp)
                    print('msgstr[1] ""\n', file=fp)
                else:
                    print('msgstr ""\n', file=fp)

def main():
    global default_keywords
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'ad:DEhk:Kno:p:S:Vvw:x:X:f:',
            ['extract-all', 'default-domain=', 'escape', 'help',
             'keyword=', 'no-default-keywords',
             'add-location', 'no-location', 'output=', 'output-dir=',
             'style=', 'verbose', 'version', 'width=', 'exclude-file=',
             'docstrings', 'no-docstrings',
             ])
    except getopt.error as msg:
        usage(1, msg)

    # for holding option values
    class Options:
        # constants
        GNU = 1
        SOLARIS = 2
        # defaults
        extractall = 0 # FIXME: currently this option has no effect at all.
        escape = 0
        keywords = ['ugettext', 'ungettext']
        outpath = ''
        outfile = 'messages.pot'
        writelocations = 1
        locationstyle = GNU
        verbose = 0
        width = 78
        excludefilename = ''
        docstrings = 0
        nodocstrings = {}

    options = Options()
    locations = {'gnu' : options.GNU,
                 'solaris' : options.SOLARIS,
                 }

    files = ''

    # parse options
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-a', '--extract-all'):
            options.extractall = 1
        elif opt in ('-d', '--default-domain'):
            options.outfile = arg + '.pot'
        elif opt in ('-E', '--escape'):
            options.escape = 1
        elif opt in ('-D', '--docstrings'):
            options.docstrings = 1
        elif opt in ('-k', '--keyword'):
            options.keywords.append(arg)
        elif opt in ('-K', '--no-default-keywords'):
            default_keywords = []
        elif opt in ('-n', '--add-location'):
            options.writelocations = 1
        elif opt in ('--no-location',):
            options.writelocations = 0
        elif opt in ('-S', '--style'):
            options.locationstyle = locations.get(arg.lower())
            if options.locationstyle is None:
                usage(1, ('Invalid value for --style: %s') % arg)
        elif opt in ('-o', '--output'):
            options.outfile = arg
        elif opt in ('-p', '--output-dir'):
            options.outpath = arg
        elif opt in ('-v', '--verbose'):
            options.verbose = 1
        elif opt in ('-V', '--version'):
            print(('pygettext.py (xgettext for Python) %s') % __version__)
            sys.exit(0)
        elif opt in ('-w', '--width'):
            try:
                options.width = int(arg)
            except ValueError:
                usage(1, ('--width argument must be an integer: %s') % arg)
        elif opt in ('-x', '--exclude-file'):
            options.excludefilename = arg
        elif opt in ('-X', '--no-docstrings'):
            fp = open(arg)
            try:
                while 1:
                    line = fp.readline()
                    if not line:
                        break
                    options.nodocstrings[line[:-1]] = 1
            finally:
                fp.close()
        elif opt == '-f':
            files = arg

    # calculate escapes
#    make_escapes(options.escape)

    # calculate all keywords
    options.keywords.extend(default_keywords)

    # initialize list of strings to exclude
    if options.excludefilename:
        try:
            fp = open(options.excludefilename)
            options.toexclude = fp.readlines()
            fp.close()
        except IOError:
            print((
                "Can't read --exclude-file: %s") % options.excludefilename, file=sys.stderr)
            sys.exit(1)
    else:
        options.toexclude = []

    # resolve args to module lists
    expanded = []
    for arg in args:
        if arg == '-':
            expanded.append(arg)
        else:
            expanded.extend(getFilesForName(arg))
    args = expanded

    if files:
        lines = open(files).readlines()
        for line in lines:
            args.append(line.strip())

    # slurp through all the files
    eater = TokenEater(options)
    for filename in args:
        if filename == '-':
            if options.verbose:
                print ('Reading standard input')
            fp = sys.stdin
            closep = 0
        else:
            if options.verbose:
                print(('Working on %s') % filename)
            if filename.endswith('.html'):
                from uliweb.core.template import template_file_py
                from io import StringIO
                text = template_file_py(filename, skip_extern=True, multilines=True)
                fp = StringIO(text)
            else:
                fp = open(filename)
                closep = 1
        try:
            eater.set_filename(filename)
            try:
                tokenize.tokenize(fp.readline, eater)
            except tokenize.TokenError as e:
                print('%s: %s, line %d, column %d' % (
                    e[0], filename, e[1][0], e[1][1]), file=sys.stderr)
        finally:
            if closep:
                fp.close()

    # write the output
    if options.outfile == '-':
        fp = sys.stdout
        closep = 0
    else:
        if options.outpath:
            options.outfile = os.path.join(options.outpath, options.outfile)
        path = os.path.dirname(options.outfile)
        if path:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    pass
        fp = open(options.outfile, 'w')
        closep = 1
    try:
        eater.write(fp)
    finally:
        if closep:
            fp.close()

def extrace_files(files, outputfile, opts=None, vars=None):
    global _py_ext
    import logging
    from io import StringIO, BytesIO

    log = logging.getLogger('pygettext')
    
    opts = opts or {}
    vars = vars or {}
    
    _py_ext = ['.py', '.ini', '.html']
    class Options:
        # constants
        GNU = 1
        SOLARIS = 2
        # defaults
        extractall = 0 # FIXME: currently this option has no effect at all.
        escape = 0
        keywords = ['_', 'gettext', 'ngettext', 'ungettext', 'ugettext']
        outpath = ''
        outfile = outputfile
        writelocations = 1
        locationstyle = GNU
        verbose = 0
        width = 78
        excludefilename = ''
        docstrings = 0
        nodocstrings = {}
        toexclude = []

    options = Options()

#    make_escapes(options.escape)
    options.keywords.extend(default_keywords)
    for k, v in opts.items():
        if v and hasattr(options, k):
            _v = getattr(options, k)
            if isinstance(_v, list):
                _v.extend(v)
            elif isinstance(_v, dict):
                _v.update(v)
            else:
                setattr(options, k, v)
    
    if not isinstance(files, list):
        files = getFilesForName(files)
    eater = TokenEater(options, vars=vars)
    for filename in files:
        if options.verbose:
            print(('Working on %s') % filename)
        if not os.path.exists(filename):
            continue
        if filename.endswith('.html'):
            from uliweb.core import template
            from uliweb.core.template import template_file_py
            text = template_file_py(filename, skip_extern=True, log=log, multilines=True)
            fp = BytesIO(b(text))
            closep = 0
        else:
            fp = BytesIO(b(open(filename).read()))
            closep = 1
        
        try:
            eater.set_filename(filename)
            try:
                for v in tokenize.tokenize(fp.readline):
                    eater(*v)
            except tokenize.TokenError as e:
                print('%s: %s, line %d, column %d' % (
                    e[0], filename, e[1][0], e[1][1]), file=sys.stderr)
        finally:
            if closep:
                fp.close()
    
    if options.outfile == '-':
        fp = sys.stdout
        closep = 0
    else:
        if options.outpath:
            options.outfile = os.path.join(options.outpath, options.outfile)
        path = os.path.dirname(options.outfile)
        if path:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    pass
        fp = open(options.outfile, 'w')
        closep = 1
    try:
        eater.write(fp)
    finally:
        if closep:
            fp.close()

if __name__ == '__main__':
    main()
    # some more test strings
#    _(u'a unicode string')
#    # this one creates a warning
#    _('*** Seen unexpected token "%(token)s"') % {'token': 'test'}
#    _('more' 'than' 'one' 'string')
