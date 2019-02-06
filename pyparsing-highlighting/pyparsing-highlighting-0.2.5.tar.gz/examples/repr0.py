"""A Python repr() syntax highlighter."""

from prompt_toolkit.styles import Style
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from .repl import repl


# pylint: disable=too-many-locals
def parser_factory(styler):
    """Builds the repr() parser."""
    squo = styler('class:string', "'")
    dquo = styler('class:string', '"')

    esc_single = pp.oneOf(r'\\ \' \" \n \r \t')
    esc_hex = pp.Literal(r'\x') + pp.Word(pp.hexnums, exact=2)
    escs = styler('class:escape', esc_single | esc_hex)

    control_chars = ''.join(map(chr, range(32))) + '\x7f'
    normal_chars_squo = pp.CharsNotIn(control_chars + r"\'")
    chars_squo = styler('class:string', normal_chars_squo) | escs
    normal_chars_dquo = pp.CharsNotIn(control_chars + r'\"')
    chars_dquo = styler('class:string', normal_chars_dquo) | escs

    skip_white = pp.Optional(pp.White())
    bytes_prefix = pp.Optional(styler('class:string_prefix', 'b'))
    string_squo = skip_white + bytes_prefix + squo - pp.ZeroOrMore(chars_squo) + squo
    string_dquo = skip_white + bytes_prefix + dquo - pp.ZeroOrMore(chars_dquo) + dquo
    string = string_squo | string_dquo
    string.leaveWhitespace()

    value = pp.Forward()

    lst = '[' - pp.Optional(pp.delimitedList(value) + pp.Optional(',')) + ']'
    tpl = '(' - pp.Optional(pp.delimitedList(value) + pp.Optional(',')) + ')'
    pair = value + ':' - value
    dct = '{' - pp.Optional(pp.delimitedList(pair) + pp.Optional(',')) + '}'
    number = styler('class:number', ppc.number)
    const = pp.oneOf('True False None NotImplemented Ellipsis ...')
    const = styler('class:constant', const)

    kwarg = styler('class:kwarg', ppc.identifier) + styler('class:operator', '=') - value
    args = pp.Optional(pp.delimitedList(value | kwarg) + pp.Optional(','))
    call = styler('class:call', ppc.identifier) + '(' - args + ')'

    obj = pp.Forward()
    obj <<= '<' - pp.ZeroOrMore(obj | pp.CharsNotIn('<>')) + '>'

    value <<= lst | tpl | dct | number | string | const | call | obj
    value.parseWithTabs()
    return pp.originalTextFor(value)


def main():
    """The main function."""
    style = Style([
        ('call', '#4078f2'),
        ('constant', '#b27a01 bold'),
        ('escape', '#0092c7'),
        ('kwarg', '#b27a01 italic'),
        ('number', '#b27a01'),
        ('operator', '#b625b4 bold'),
        ('string', '#528f50'),
        ('string_prefix', '#528f50 bold'),
    ])
    repl(parser_factory, style=style)


if __name__ == '__main__':
    main()
