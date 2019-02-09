# coding=utf-8

'''
read/write .properties file in a simple line-oriented format.

Note: the code takes Java class `java.util.Properties` for reference.

properties data are key-value pairs stored in a dictionary.

common usage in file I/O:

properties = load(file)
store(file, properties)

main features:
* seperate key and value by one of `=`, `:`, ` `, `\\t`
* ignore whitespaces leading in a line or around `=` or `:`
* comment line begin with `#` or `!`
* escape unicode by `\\uxxxx`
* escape special characters by adding `\\`

others:
* data line ends with '\\' discard the line break

differences with Java:
* store method will not write datetime comment
'''

import os
import re
import sys

# 兼容 python3
if sys.version_info.major == 3:
    def hasNext(o):
        return hasattr(o, '__next__')
    xrange = range
else:
    def hasNext(o):
        return hasattr(o, 'next')
    def next(o):
        return o.next()

def load(iterable, properties=None):
    '''
    read properties in line-oriented format and store in the dictionary.

    Note: key and value will be of unicode type if the input data
    has \\uxxxx that will be decoded as unicode char.

    @param  iterable    a iterable object to get `str` data
                        (normally the file object)
    @param  properties  dictionary to store data,
                        defaults None and the data with return
    @return             dictionary stores the key-value data

    @call  class LineReader
    @call  #loadSingle(string)

    ---detail from Java document---
     * Properties are processed in terms of lines. There are two
     * kinds of line, natural lines and logical lines.
     * A natural line is defined as a line of
     * characters that is terminated either by a set of line terminator
     * characters ('\\n' or '\\r' or '\\r\\n')
     * or by the end of the stream. A natural line may be either a blank line,
     * a comment line, or hold all or some of a key-element pair. A logical
     * line holds all the data of a key-element pair, which may be spread
     * out across several adjacent natural lines by escaping
     * the line terminator sequence with a backslash character
     * '\\'.  Note that a comment line cannot be extended
     * in this manner; every natural line that is a comment must have
     * its own comment indicator, as described below. Lines are read from
     * input until the end of the *iteration* is reached.
     * 
     * A natural line that contains only white space characters is
     * considered blank and is ignored.  A comment line has an ASCII
     * '#' or '!' as its first non-white
     * space character; comment lines are also ignored and do not
     * encode key-element information.  In addition to line
     * terminators, this format considers the characters space
     * (' '), tab
     * ('\\t'), and form feed
     * ('\\f') to be white
     * space.
     * 
     * If a logical line is spread across several natural lines, the
     * backslash escaping the line terminator sequence, the line
     * terminator sequence, and any white space at the start of the
     * following line have no affect on the key or element values.
     * The remainder of the discussion of key and element parsing
     * (when loading) will assume all the characters constituting
     * the key and element appear on a single natural line after
     * line continuation characters have been removed. Note that
     * it is not sufficient to only examine the character
     * preceding a line terminator sequence to decide if the line
     * terminator is escaped; there must be an odd number of
     * contiguous backslashes for the line terminator to be escaped.
     * Since the input is processed from left to right, a
     * non-zero even number of 2n contiguous backslashes
     * before a line terminator (or elsewhere) encodes n
     * backslashes after escape processing.
     * 
     * The key contains all of the characters in the line starting
     * with the first non-white space character and up to, but not
     * including, the first unescaped '=',
     * ':', or white space character other than a line
     * terminator. All of these key termination characters may be
     * included in the key by escaping them with a preceding backslash
     * character; for example,
     * 
     * \\:\\=
     * 
     * would be the two-character key ":=".  Line
     * terminator characters can be included using \\r and
     * \\n escape sequences. Any white space after the
     * key is skipped; if the first non-white space character after
     * the key is '=' or ':', then it is
     * ignored and any white space characters after it are also
     * skipped.  All remaining characters on the line become part of
     * the associated element string; if there are no remaining
     * characters, the element is the empty string
     * "".  Once the raw character sequences
     * constituting the key and element are identified, escape
     * processing is performed as described above.
     * 
     * As an example, each of the following three lines specifies the key
     * "Truth" and the associated element value
     * "Beauty":
     * 
     * Truth = Beauty
     *  Truth:Beauty
     * Truth                    :Beauty
     * 
     * As another example, the following three lines specify a single
     * property:
     * 
     * fruits                           apple, banana, pear, \
     *                                  cantaloupe, watermelon, \
     *                                  kiwi, mango
     *
     * The key is "fruits" and the associated element is:
     * "apple, banana, pear, cantaloupe, watermelon, kiwi, mango"
     * Note that a space appears before each '\\' so that a space
     * will appear after each comma in the final result; the '\\',
     * line terminator, and leading white space on the continuation line are
     * merely discarded and are not replaced by one or more other
     * characters.
     * 
     * As a third example, the line:
     * cheeses
     * 
     * specifies that the key is "cheeses" and the associated
     * element is the empty string "".
     * 
     * Characters in keys and elements can be represented in escape
     * sequences similar to those used for character and string literals
     * (see sections 3.3 and 3.10.6 of
     * The Java™ Language Specification).
     *
     * The differences from the character escape sequences and Unicode
     * escapes used for characters and strings are:
     *
     *  *   Octal escapes are not recognized.
     *
     *  *   The character sequence '\\b' does not
     *      represent a backspace character.
     *
     *  *   The method does not treat a backslash character,
     *      '\\', before a non-valid escape character as an
     *      error; the backslash is silently dropped.  For example, in a
     *      Java string the sequence "\\z" would cause a
     *      compile time error.  In contrast, this method silently drops
     *      the backslash.  Therefore, this method treats the two character
     *      sequence "\\b" as equivalent to the single
     *      character 'b'.
     *
     *  *   Escapes are not necessary for single and double quotes;
     *      however, by the rule above, single and double quote characters
     *      preceded by a backslash still yield single and double quote
     *      characters, respectively.
     *
     *  *   Only a single 'u' character is allowed in a Unicode escape
     *      sequence.
    '''
    if properties == None:
        properties = {}
    for line in LineReader(iterable):
        key, value = loadSingle(line)
        properties[key] = value
    return properties

def loadSingle(string):
    '''
    read a key-value pair from data of one key-value.
    this identifies the key and value, seperates them and does escape processing.

    Note: to provide independent use, this first skips leading whitespaces
    which will normally be done by LineReader.

    @example
    loadSingle('key = value') -> 'key', 'value'

    @param  string  one data of key-value pair
    @return key, value

    @call  #identifyKeyValue(line)
    @call  #loadConvert(inp, off, length)

    @see  load(iterable, properties=None)
    '''
    for i in xrange(len(string)):
        if string[i] == ' ' or string[i] == '\t' or string[i] == '\f':
            continue
        break
    if i > 0:
        string = string[i:]
    keyEnd, valueStart = identifyKeyValue(string)
    key = loadConvert(string, 0, keyEnd)
    value = loadConvert(string, valueStart, len(string) - valueStart)
    return key, value

_loadSingle2_pattern = re.compile(r'^[ \t\f]*((?:\\\\|\\=|\\:|[^ \t\f])+?)(?:[ \t\f]*(?::|=)[ \t\f]*|[ \t\f]+)([\s\S]*)$')

def loadSingle2(string):
    '''
    regex implement
    '''
    for i in xrange(len(string)):
        if string[i] == ' ' or string[i] == '\t' or string[i] == '\f':
            continue
        break
    if i > 0:
        string = string[i:]
    m = re.search(_loadSingle2_pattern, string)
    key = loadConvert(m.group(1))
    value = loadConvert(m.group(2))
    return key, value

def identifyKeyValue(string):
    '''
    identify key-end and value-start position
    from data start immediately with the key.

    the data should not have leading whitespace
    since whitespace will be read as seperator,
    then the key will be empty.

    @example
    identifyKeyValue('key=value') -> 3, 4
    identifyKeyValue('key = value') -> 3, 6
    '''
    limit = len(string)
    keyEnd = 0
    valueStart = limit
    hasSep = False
    precedingBackslash = False
    while (keyEnd < limit):
        c = string[keyEnd]
        # need check if escaped.
        if (c == '=' or  c == ':') and not precedingBackslash:
            valueStart = keyEnd + 1
            hasSep = True
            break
        elif ((c == ' ' or c == '\t' or  c == '\f') and
              not precedingBackslash):
            valueStart = keyEnd + 1
            break
        if c == '\\':
            precedingBackslash = not precedingBackslash
        else:
            precedingBackslash = False
        keyEnd += 1
    while (valueStart < limit):
        c = string[valueStart]
        if c != ' ' and c != '\t' and  c != '\f':
            if not hasSep and (c == '=' or  c == ':'):
                hasSep = True
            else:
                break
        valueStart += 1
    return keyEnd, valueStart

def loadConvert(string, off=0, length=None):
    '''
    Converts encoded \\uxxxx to unicode chars
    and changes special saved chars to their original forms

    @example
    loadConvert('\\==', 0, 2) -> '='

    @param  string  string to process
    @param  off     offset, the beginning index to process, defaults 0
    @param  length  length of the string begin from offset to process,
                    defaults to process to the end
    @return         processed string
    '''
    out = []
    if length == None:
        end = len(string)
    else:
        end = off + length
    while (off < end):
        aChar = string[off]
        off += 1
        if aChar == '\\':
            aChar = string[off]
            off += 1
            if aChar == 'u':
                aChar = (u'\\u' + string[off:off+4]).encode().decode('unicode-escape')
                off += 4
            else:
                if aChar == 't': aChar = '\t'
                elif aChar == 'r': aChar = '\r'
                elif aChar == 'n': aChar = '\n'
                elif aChar == 'f': aChar = '\f'
        out.append(aChar)
    return ''.join(out)

def _loadConvert2_func(m):
    s = m.group()
    if s[1] == 'u':
        return s.encode().decode('unicode-escape')
    if s[1] == 't':
        return '\t'
    if s[1] == 'r':
        return '\r'
    if s[1] == 'n':
        return '\n'
    if s[1] == 'f':
        return '\f'
    return s[1]
_loadConvert2_pattern = re.compile(r'\\(u....|[^\r\n])')

def loadConvert2(string):
    '''
    regex implement
    '''
    return re.sub(_loadConvert2_pattern, _loadConvert2_func, string)


def storeConvert(unic, escapeSpace=True, escapeUnicode=True):
    '''
    Converts unicodes to encoded \\uxxxx and escapes
    special characters with a preceding slash

    Note: the return is unicode type if the input is.

    @param  unic            input string
    @param  escapeSpace     True for key, False for value (true is OK)
    @param  escapeUnicode   (boolean)
    @return                 processed string
    '''
    outBuffer = []
    for x in range(len(unic)):
        aChar = unic[x]
        # Handle common case first, selecting largest block that
        # avoids the specials below
        if ord(aChar) > 61 and ord(aChar) < 127:
            if aChar == '\\':
                outBuffer.append('\\\\')
                continue
            outBuffer.append(aChar)
            continue
        if aChar == ' ':
            if x == 0 or escapeSpace:
                outBuffer.append('\\')
            outBuffer.append(' ')
        elif aChar == '\t':
            outBuffer.append('\\t')
        elif aChar == '\n':
            outBuffer.append('\\n')
        elif aChar == '\r':
            outBuffer.append('\\r')
        elif aChar == '\f':
            outBuffer.append('\\f')
        elif aChar == '=' or aChar == ':' or aChar == '#' or aChar == '!':
            outBuffer.append('\\' + aChar)
        else:
            if (((ord(aChar) < 0x0020) or (ord(aChar) > 0x007e))
                and escapeUnicode):
                outBuffer.append('\\u%04x' % ord(aChar))
            else:
                outBuffer.append(aChar)
    return ''.join(outBuffer)

def storeComments(writable, comments, linesep=os.linesep):
    '''
    write comments with writable.write(str).

    @param  writable    object with method write(str)
    @param  comments    string of comments
    @param  linesep     line terminator (seperator) '\\n' or '\\r' or '\\r\\n',
                        defaults os.linesep

    @see  #store(writable, properties, comments=None)
    '''
    writable.write("#")
    length = len(comments)
    current = 0
    last = 0
    while (current < length):
        c = comments[current]
        if ord(c) > 0x00ff or c == '\n' or c == '\r':
            if last != current:
                writable.write(comments[last:current])
            if ord(c) > 0x00ff:
                writable.write(c.encode('unicode-escape').decode())
            else:
                writable.write(linesep)
                if (c == '\r' and \
                    current != length - 1 and \
                    comments[current + 1] == '\n'):
                    current += 1
                if (current == length - 1 or
                    (comments[current + 1] != '#' and
                    comments[current + 1] != '!')):
                    writable.write("#")
            last = current + 1
        current += 1
    if last != current:
        writable.write(comments[last:current])
    writable.write(linesep)

def store(writable, properties, comments=None):
    '''
    writes the comments, properties keys and values in line-oriented format
    with writable.write(str).

    keys and values must be string.

    @param  writable    object with method write(str)
    @param  properties  a dictionary stores properties
    @param  comments    string comments to write before the properties
                        defaults None and no comment is written

    @call  #storeComments(writable, comments, linesep=os.linesep)
    @call  #storeSingle(writable, key, value, sep='=', linesep=os.linesep)

    ---detail from Java document---
     * If the comments argument is not null, then an ASCII '#'
     * character, the comments string, and a line separator are first written
     * to the output stream. Thus, the comments can serve as an
     * identifying comment. Any one of a line feed ('\\n'), a carriage
     * return ('\\r'), or a carriage return followed immediately by a line feed
     * in comments is replaced by a line separator generated by os.linesep
     * and if the next character in comments is not character '#' or
     * character '!' then an ASCII '#' is written out
     * after that line separator.
     * 
     * Then every entry in this properties is
     * written out, one per line. For each entry the key string is
     * written, then an ASCII '=', then the associated
     * element string. For the key, all space characters are
     * written with a preceding '\\' character.  For the
     * element, leading space characters, but not embedded or trailing
     * space characters, are written with a preceding '\\'
     * character. The key and element characters '#',
     * '!', '=', and ':' are written
     * with a preceding backslash to ensure that they are properly loaded.
     * 
     * After the entries have been written, 
     * *the writable object will not be closed*.

     *  *   The stream is written using the ISO 8859-1 character encoding.
     * 
     *  *   Characters not in Latin-1 in the comments are written as
     *      \\uxxxx for their appropriate unicode
     *      hexadecimal value 'xxxx'.

     *  *   Characters less than \\u0020 and characters greater
     *      than \\u007E in property keys or values are written
     *      as \\uxxxx for the appropriate hexadecimal
     *      value 'xxxx'.
    '''
    if comments != None:
        storeComments(writable, comments)
    for key, value in properties.items():
        storeSingle(writable, key, value)

def storeSingle(writable, key, value, sep='=', linesep=os.linesep):
    '''
    write key-value pair as one line with writable.write(str).

    key and value must be string.

    @param  writable    object with method write(str)
    @param  key         string of the key
    @param  value       string of the value
    @param  sep         key-value seperator, '=' or ':', defaults '='
    @param  linesep     line terminator (seperator) '\\n' or '\\r' or '\\r\\n',
                        defaults os.linesep

    @see  store(writable, properties, comments=None)
    '''
    key = storeConvert(key, True, True)
    #No need to escape embedded and trailing spaces for value, hence
    # pass False to flag.
    value = storeConvert(value, False, True)
    writable.write((key + sep + value).encode('Latin-1'))
    writable.write(linesep)

from collections import Iterable

class LineReader:
    '''
    @Iterable
    read in data of one key-value pair each time from raw input.

    the return data has no leading whitespace or line terminator.

    @example
    for line in LineReader(file):
        pass

    @see  #load(iterable, properties=None)

    ---detail from Java document---
     * Read in a "logical line" from an *iterable object*, skip all comment
     * and blank lines and filter out those leading whitespace characters
     * (\\u0020, \\u0009 and \\u000c) from the beginning of a "natural line".
     '''
    def __init__(self, iterable):
        if hasNext(iterable):
            self.iterator = iterable
        elif isinstance(iterable, Iterable):
            self.iterator = iter(iterable)
        else:
            raise TypeError('\'' + str(type(iterable))
                            + '\' object is not iterable')
        self.inLimit = 0
        self.inOff = 0

    def __iter__(self):
        return self

    def next(self):
        lineBuf = []
        leng = 0

        skipWhiteSpace = True
        isCommentLine = False
        isNewLine = True
        appendedLineBegin = False
        precedingBackslash = False
        skipLF = False

        while (1):
            if self.inOff >= self.inLimit:
                try:
                    self.inByteBuf = next(self.iterator)
                    self.inLimit = len(self.inByteBuf)
                except StopIteration as e:
                    self.inLimit = -1
                self.inOff = 0
                if self.inLimit <= 0:
                    if leng == 0 or isCommentLine:
                        raise StopIteration()
                    if precedingBackslash:
                        lineBuf.pop()
                        leng -= 1
                    return ''.join(lineBuf)
            c = self.inByteBuf[self.inOff:self.inOff+1]
            self.inOff += 1
            if skipLF:
                skipLF = False
                if c == '\n':
                    continue
            if skipWhiteSpace:
                if c == ' ' or c == '\t' or c == '\f':
                    continue
                if not appendedLineBegin and (c == '\r' or c == '\n'):
                    continue
                skipWhiteSpace = False
                appendedLineBegin = False
            if isNewLine:
                isNewLine = False
                if c == '#' or c == '!':
                    isCommentLine = True
                    continue

            if c != '\n' and c != '\r':
                if leng == 0:
                    lineBuf = []
                lineBuf.append(c)
                leng += 1
                #flip the preceding backslash flag
                if c == '\\':
                    precedingBackslash = not precedingBackslash
                else:
                    precedingBackslash = False
            else:
                # reached EOL
                if isCommentLine or leng == 0:
                    isCommentLine = False
                    isNewLine = True
                    skipWhiteSpace = True
                    leng = 0
                    continue
                if self.inOff >= self.inLimit:
                    try:
                        self.inByteBuf = next(self.iterator) # read a line
                        self.inLimit = len(self.inByteBuf)
                    except Exception as e:
                        self.inLimit = -1
                    self.inOff = 0
                    if self.inLimit <= 0:
                        if precedingBackslash:
                            lineBuf.pop()
                            leng -= 1
                        return ''.join(lineBuf)
                if precedingBackslash:
                    lineBuf.pop()
                    leng -= 1
                    #skip the leading whitespace characters in following line
                    skipWhiteSpace = True
                    appendedLineBegin = True
                    precedingBackslash = False
                    if c == '\r':
                        skipLF = True
                else:
                    return ''.join(lineBuf)
LineReader.__next__ = LineReader.next

class LineReader2:
    '''
    implement by regex

    @see  LineReader
    '''
    def __init__(self, iterable):
        self.iterator = NormalLineReader2(iterable)
        # self.inByteBuf = '' # byte[] -> string

        # in Window, package re only recognizes '\\n' as the line terminator,
        # this influence '^' and '$' so I write it by myself.

        # find a (multi-line) key-value, ignore blank lines or comments
        self.r = re.compile(r'(?:^|(?<=\r|\n))[ \t\f]*[^#! \t\f\r\n][\s\S]*?(?<!\\)(?:\\\\)*(?=\r\n|\r|(?<!\r)\n)')
        # find leading whiespaces each line for replacement
        self.r2 = re.compile(r'(?:^|(?<=\r|\n))[ \t\f]*')
        # find backslashes followed by the line terminator for replacement
        self.r3 = re.compile(r'\\(?:\r\n|\n|\r)')
        # find single backslashes at the end (odd number) for replacement
        self.r4 = re.compile(r'((?<!\\)(?:\\\\)*)\\$')

    def __iter__(self):
        return self

    def next(self):
        buf = '' # buffer
        while 1:
            try:
                buf += next(self.iterator) # read a line
            except StopIteration as e:
                if buf == '':
                    raise e
                buf += '\n' # regex search dependent on the line terminator, it may be lost at the end of file
            m = re.search(self.r, buf)
            if m != None:
                buf = re.sub(self.r2, '', m.group())
                buf = re.sub(self.r3, '', buf)
                buf = re.sub(self.r4, lambda x:x.group(1), buf)
                if buf != '': # may have blank line
                    return buf
LineReader2.__next__ = LineReader2.next

class NormalLineReader2:
    '''
    @Iterable
    read from raw input, read in one line each time,
    including the line terminator '\\r' or '\\n' or '\\r\\n'

    implement by regex
    '''
    def __init__(self, iterable):
        if hasNext(iterable):
            self.iterator = iterable
        elif isinstance(iterable, Iterable):
            self.iterator = iter(iterable)
        else:
            raise TypeError('\'' + str(type(iterable))
                            + '\' object is not iterable')
        self.inByteBuf = '' # byte[] -> string

        self.r = re.compile(r'^(?P<line>[^\r\n]*(?:\r\n|\r(?=[^\n])|\n))(?P<left>[\s\S]*)$')

    def __iter__(self):
        return self

    def next(self):
        left = None
        while 1:
            m = re.search(self.r, self.inByteBuf)
            if m != None and m.lastindex > 1:
                self.inByteBuf = m.group('left')
                return m.group('line')
            if left:
                return left
            try:
                self.inByteBuf += next(self.iterator)
            except StopIteration as e:
                if len(self.inByteBuf) == 0:
                    raise e
                left = self.inByteBuf
                self.inByteBuf = ''
NormalLineReader2.__next__ = NormalLineReader2.next
