"""An example :func:`repr()` parser."""

# pylint: disable=too-many-locals

from functools import reduce
from itertools import chain

from prompt_toolkit.styles import Style
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from pp_highlighting import dummy_styler
from .repl import repl


class Call:
    """Represents a function call."""
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        args_map = map(repr, self.args)
        kwargs_map = map('{}={}'.format, self.kwargs, self.kwargs.values())
        return '{}({})'.format(self.name, ', '.join(chain(args_map, kwargs_map)))


class Identifier:
    """Represents an identifier."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Attr:
    """Represents an attribute reference."""
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    def __repr__(self):
        return '{!r}.{!r}'.format(self.obj, self.name)


class Slicing:
    """Represents a slicing."""
    def __init__(self, obj, slice_list):
        self.obj = obj
        self.slice_list = slice_list

    def __repr__(self):
        return '{!r}[{}]'.format(self.obj, ', '.join(map(repr, self.slice_list)))


class ParenExpr:
    """Represents a parenthesized expression."""
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '({!r})'.format(self.expr)


def parser_factory(styler=dummy_styler):
    """Builds the :func:`repr()` parser."""
    # def cond_optional(expr):
    #     return pp.Optional(expr) if styler else expr

    (LPAR, RPAR, LBRK, RBRK, LBRC,
     RBRC, COMMA, DOT, COLON) = map(pp.Suppress, '()[]{},.:')
    EQ = styler('class:operator', pp.Suppress('='))
    OCOMMA = pp.Optional(COMMA)

    atom = pp.Forward()

    number = styler('class:number', ppc.number)

    constant_mapping = {'True': True, 'False': False, 'None': None,
                        'Ellipsis': Ellipsis, '...': Ellipsis,
                        'NotImplemented': NotImplemented}
    constant = styler('class:constant', pp.oneOf(' '.join(constant_mapping)))
    constant.addParseAction(lambda t: [constant_mapping[t[0]]])

    string = styler('class:string', pp.quotedString)
    string.addParseAction(lambda t: t[0][1:-1])

    atom_list = atom + pp.ZeroOrMore(COMMA + atom)
    list_expr = LBRK + pp.Optional(atom_list + OCOMMA) + RBRK
    list_expr.addParseAction(lambda t: [list(t)])

    dict_item = pp.Group(atom + COLON + atom)
    dict_items = dict_item + pp.ZeroOrMore(COMMA + dict_item)
    dict_expr = LBRC + pp.Dict(pp.Optional(dict_items + OCOMMA)) + RBRC
    dict_expr.addParseAction(lambda t: [dict(list(t))])

    call_name = styler('class:call', ppc.identifier)
    call_args = atom + pp.ZeroOrMore(COMMA + atom + ~EQ)
    call_kwarg = pp.Group(styler('class:parameter', ppc.identifier) + EQ + atom)
    call_kwargs = pp.Dict(call_kwarg + pp.ZeroOrMore(COMMA + call_kwarg))
    call_kwargs.addParseAction(lambda t: t.asDict())
    call_allargs = call_kwargs | call_args + pp.Optional(COMMA + call_kwargs)
    call = call_name + LPAR + pp.Optional(call_allargs + OCOMMA) + RPAR
    def do_call(t):
        if len(t) == 1:
            return Call(t[0])
        if isinstance(t[-1], dict):
            return Call(t[0], *t[1:-1], **t[-1])
        return Call(t[0], *t[1:])
    call.addParseAction(do_call)

    identifier = styler('class:identifier', ppc.identifier)
    identifier.addParseAction(lambda t: Identifier(t[0]))

    # paren_expr = (LPAR + (primary | atom) + RPAR).addParseAction(lambda t: ParenExpr(t[0]))
    primary_lhs = constant | string | list_expr | dict_expr | call | identifier
    attr_rhs = DOT + identifier
    attr_rhs.addParseAction(lambda t: lambda x: Attr(x, t[0]))
    call_rhs = LPAR + pp.Optional(call_allargs + OCOMMA) + RPAR
    call_rhs.addParseAction(lambda t: lambda x: do_call([x] + list(t)))
    slicing_rhs = LBRK + atom + pp.ZeroOrMore(COMMA + atom) + RBRK
    slicing_rhs.addParseAction(lambda t: lambda x: Slicing(x, list(t)))
    primary = primary_lhs + pp.ZeroOrMore(attr_rhs | call_rhs | slicing_rhs)
    primary.addParseAction(lambda t: [reduce(lambda x, y: y(x), t)])

    atom <<= number | primary

    atom.validate()
    return atom


def main():
    """The main function."""
    parser = parser_factory()
    style = Style.from_dict({
        'call': '#4078f2',
        'constant': '#b27a01 bold',
        'number': '#b27a01',
        'operator': '#0092c7',
        'parameter': '#b27a01 italic',
        'string': '#528f50',
    })
    repl(parser, parser_factory, style=style)


if __name__ == '__main__':
    main()
