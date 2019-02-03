# pylint: disable=unused-argument
import re
from functools import wraps
from .structs import ConfigDict, ConfigValue


def matcher(regex):
    '''
    Wrapper around a regex that always returns the
    group dict if there is a match.

    This requires that all regex have named groups.

    '''
    rx = re.compile(regex, re.I)

    # pylint: disable=inconsistent-return-statements
    def _matcher(line):
        m = rx.match(line)
        if m:
            return m.groupdict()

    return _matcher


def substituter(regex, sub):
    rx = re.compile(regex, re.I)

    def _substituter(line):
        line = rx.sub(sub, line)
        return line

    return _substituter


# pylint: disable=too-few-public-methods
class parser(object):
    '''
    A decorator that wraps common functioning of
    our parser functions.

    '''
    def __init__(self, rxstr):
        self.regex = matcher(rxstr)

    def __call__(self, func):

        @wraps(func)
        def _parser(line, parm):
            match = self.regex(line)
            if match:
                return func(match, line, parm)
            return line

        return _parser


@parser(r'^\[(?P<section>[^\]]+)\] *$')
def parse_section(match, line, parm):
    '''
    Any line that begins with "[" and ends with "]"
    is considered a section.

    '''
    section_name = match['section'].strip()
    section_heirarchy = section_name.split('.')
    section_dict = parm['config']
    for section in section_heirarchy:
        section_dict = section_dict.setdefault(section, ConfigDict())
    parm['current_section'] = section_dict
    return None


@parser(r'^ {0,2}(?P<key>[A-Za-z0-9_\-\./\|]+)( ?= ?|: )(?P<value>.*)$')
def parse_option(match, line, parm):
    '''
    An option is any line that begins with a `name` followed
    by an equals sign `=` followed by some value:

        name = 12
        name.subject = 12
        name/subject = 12
        name-subject = 12
        name|subject = 12
        name.subject1 = 12
        Name.Subject3 = 12

    '''
    key = match['key'].strip()
    value = match['value']
    cv = ConfigValue(value)
    parm['current_section'][key] = cv
    parm['current_option'] = cv
    return None


@parser(r'^    *(?P<value>[^#;].*)$')
def parse_multiline_opt(match, line, parm):
    '''
    Any line that is indented with 3 or more spaces is
    considered to be a continuation of the previous
    option value.

    '''
    if parm['current_option'] is not None:
        parm['current_option'].add(match['value'])
    return None


@parser(r'^ *(#|;)(?P<comment>.*)$')
def parse_comment(match, line, parm):
    '''
    Currently we're not handling comments.

    '''
    return None


def parse_unknown(line, parm):
    '''
    Any unmatched lines are ignored.

    '''
    return None


def parse(config_lines):
    '''
    `config_lines` is expected to be a list of strings.
    which will be parsed into sections and key values.

    '''
    parsers = (parse_option,
               parse_multiline_opt,
               parse_section,
               parse_comment,
               parse_unknown)

    config = ConfigDict()

    parm = {
        'config': config,
        'current_section': config,
        'current_option': None,
    }

    rmv_crlf = substituter(r'[\r\n]', '')

    while config_lines:

        line = rmv_crlf(config_lines.pop(0))

        for _parser in parsers:
            line = _parser(line, parm)

            if line is None:
                break

    return config
