# coding=utf-8

import unittest
from .core import *

class WhiteBox(unittest.TestCase):
    def test_NormalLineReader2(self):
        s = '\
a\n\
b\\\n\
c\\\\\r\
\r\n\
z\
'
        result = [
            'a\n',
            'b\\\n',
            'c\\\\\r',
            '\r\n',
            'z'
        ]
        i = 0
        for line in NormalLineReader2(s):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in NormalLineReader2([s]):
            self.assertEqual(result[i], line)
            i += 1
        
    def test_LineReader_LineReader2(self):
        s = '\
a = b\r\n\
   \t\f\\\r\n\r\n\n\
   \t\fb = b\n\
! c\n\
# c\n\
# c\\\n\
 c = \\\r\n  b\\\\\r\n\
   \td =  \tb\n\
e = b\\\r\nc\n\
  z = b\
'
        result = [
            'a = b', # normal with flag skipLF
            # skipWhiteSpace flow, escape line terminator, blank line
            'b = b', # leading whitespaces
            # continous comment lines
            # comment can not escape line terminator
            'c = b\\\\', # escape line terminator, even number of '\'
            'd =  \tb', #
            # --- regex compare tests ---
            'e = bc', # \r\n together
            'z = b', # ends with no newlines
        ]
        i = 0
        for line in LineReader(s):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in LineReader([s]):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in LineReader2(s):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in LineReader2([s]):
            self.assertEqual(result[i], line)
            i += 1

    def test_LineReader_LineReader2_2(self):
        s = '\
a = b\n\
# c\\\n\
   \te = b\\\\\\\
'
        result = [
            'a = b', # ends with comment line and '\'
            'e = b\\\\', # ends with '\'
        ]
        i = 0
        for line in LineReader(s):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in LineReader([s]):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in LineReader2(s):
            self.assertEqual(result[i], line)
            i += 1
        i = 0
        for line in LineReader2([s]):
            self.assertEqual(result[i], line)
            i += 1

    def test_loadSingle_loadSingle2(self):
        self.assertEqual(loadSingle('key value'), ('key', 'value'))
        self.assertEqual(loadSingle(' \t\fkey value'), ('key', 'value'))

        self.assertEqual(loadSingle2('key value'), ('key', 'value'))
        self.assertEqual(loadSingle2(' \t\fkey value'), ('key', 'value'))

    def test_identifyKeyValue(self):
        def test(string, v1, v2):
            result = identifyKeyValue(string)
            self.assertEqual((v1, v2), result, string + ' -> ' + str(result) + ' but except ' + str((v1, v2)))

        # single seperator
        test('key=value', 3, 4)
        test('key:value', 3, 4)
        test('key value', 3, 4)
        test('key\tvalue', 3, 4)
        test('key\fvalue', 3, 4)

        # escaped
        test('key \\=value', 3, 4)
        test('key \\ value', 3, 4)

        # whitespaces around '='
        test('key =value', 3, 5)
        test('key= value', 3, 5)
        test('key  = value', 3, 7)

        # continous whitespaces as seperator
        test('key    value', 3, 7)
        test('key  \t value', 3, 7)

        # special cases
        test('key:=value', 3, 4)
        test('key:= value', 3, 4)

    def test_loadConvert_loadConvert2(self):
        self.assertEqual(loadConvert('s'), 's')
        self.assertEqual(loadConvert('\\u005c'), '\\')
        self.assertEqual(loadConvert('\\u4e2d'), u'中')
        self.assertEqual(loadConvert('\\t'), '\t')
        self.assertEqual(loadConvert('\\r'), '\r')
        self.assertEqual(loadConvert('\\n'), '\n')
        self.assertEqual(loadConvert('\\f'), '\f')
        self.assertEqual(loadConvert('\\b'), 'b')
        self.assertEqual(loadConvert('\\a'), 'a')

        self.assertEqual(loadConvert2('s'), 's')
        self.assertEqual(loadConvert2('\\u005c'), '\\')
        self.assertEqual(loadConvert2('\\u4e2d'), u'中')
        self.assertEqual(loadConvert2('\\t'), '\t')
        self.assertEqual(loadConvert2('\\r'), '\r')
        self.assertEqual(loadConvert2('\\n'), '\n')
        self.assertEqual(loadConvert2('\\f'), '\f')
        self.assertEqual(loadConvert2('\\b'), 'b')
        self.assertEqual(loadConvert2('\\a'), 'a')

    def test_storeConvert(self):
        self.assertEqual(storeConvert('\\'), '\\\\')
        self.assertEqual(storeConvert('  '), '\\ \\ ')
        self.assertEqual(storeConvert(' ', False), '\\ ')
        self.assertEqual(storeConvert('  ', False), '\\  ')
        self.assertEqual(storeConvert('\t'), '\\t')
        self.assertEqual(storeConvert('\n'), '\\n')
        self.assertEqual(storeConvert('\r'), '\\r')
        self.assertEqual(storeConvert('\f'), '\\f')
        self.assertEqual(storeConvert('='), '\\=')
        self.assertEqual(storeConvert(':'), '\\:')
        self.assertEqual(storeConvert('#'), '\\#')
        self.assertEqual(storeConvert('!'), '\\!')
        self.assertEqual(storeConvert(u'\u0019'), '\\u0019')
        self.assertEqual(storeConvert(u'\u00ff'), '\\u00ff')
        self.assertEqual(storeConvert(u'\u00ff', escapeUnicode=False), u'\xff')
        self.assertEqual(storeConvert(u'\u2eff', escapeUnicode=False), u'\u2eff')
        self.assertEqual(storeConvert(u'中'), '\\u4e2d')

    def test_storeComments(self):
        import os
        ls = os.linesep
        class Writer():
            def __init__(self):
                self.buf = ''
            def write(self, s):
                self.buf += s
        def test(string, *args):
            w = Writer()
            storeComments(w, string)
            lines = list(args)
            lines.append('')
            self.assertEqual(w.buf, ls.join(lines))
        test('a', '#a')
        test(u'\u4e2d', '#\\u4e2d')
        test('\r', '#', '#')
        test('\n', '#', '#')
        test('\r\n', '#', '#')
        test('\r\n#', '#', '#')
        test('\r\n!', '#', '!')
        test('\r\n #', '#', '# #')

if __name__ == '__main__':
    unittest.main()
