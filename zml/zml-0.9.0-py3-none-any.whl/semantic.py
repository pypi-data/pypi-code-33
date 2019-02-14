import math
from pyparsing import *
import operator


exprStack = []

variables = {}


def pushFirst(strg, loc, toks):
    exprStack.append(toks[0])


def pushUMinus(strg, loc, toks):
    for t in toks:
        if t == '-':
            exprStack.append('unary -')
            # ~ exprStack.append( '-1' )
            # ~ exprStack.append( '*' )
        else:
            break


bnf = None


def BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        # point = Literal(".")
        e = CaselessLiteral("E")
        # ~ fnumber = Combine( Word( "+-"+nums, nums ) +
        # ~ Optional( point + Optional( Word( nums ) ) ) +
        # ~ Optional( e + Word( "+-"+nums, nums ) ) )
        fnumber = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
        ident = Word(alphas, alphas + nums + "_$")

        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")

        expr = Forward()
        atom = ((0, None) * minus + (pi | e | fnumber | ident + lpar + expr + rpar | ident).setParseAction(pushFirst) | Group(lpar + expr + rpar)).setParseAction(pushUMinus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left
        # exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))

        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
        bnf = expr
    return bnf


# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = {"+": operator.add,
       "-": operator.sub,
       "*": operator.mul,
       "/": operator.truediv,
       "^": operator.pow}
fn = {"sin": math.sin,
      "cos": math.cos,
      "tan": math.tan,
      "abs": abs,
      "trunc": lambda a: int(a),
      "round": round,
      "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}


def evaluateStack(s):
    op = s.pop()
    if op == 'unary -':
        return -evaluateStack(s)
    if op in "+-*/^":
        op2 = evaluateStack(s)
        op1 = evaluateStack(s)
        return opn[op](op1, op2)
    elif op == "PI":
        return math.pi  # 3.1415926535
    elif op == "E":
        return math.e  # 2.718281828
    elif op in fn:
        return fn[op](evaluateStack(s))
    elif op[0].isalpha():
        if op in variables:
            return variables[op]
        raise Exception("invalid identifier '%s'" % op)
    elif '.' in op:
            return float(op)
    else:
        return int(op)


def named(marker):
    def parse_action_impl(s, l, t):
        return (marker, t)
    return parse_action_impl


void_elements = [
    '', 'area', 'base', 'br', 'col', 'command',
    'embed', 'hr', 'img', 'input', 'keygen',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
]

inline_elements = [
    'h1', 'a', 'b', 'strong', 'i', 'em', 'title', 'label', 'button'
]


# general node semantics

ARITH_EXPRESSION = BNF()
COLON = Literal(':')

UNQUOTED_WORDS = Word(printables + ' ', excludeChars="'{}<>")

DESCRIPTOR = Word(alphanums + '_')
NAMESPACE_DESCRIPTOR = DESCRIPTOR('namespace') + '-' + DESCRIPTOR('namespaced_descriptor')
GLYPH = Word('*$&~!+%#@', max=1)('glyph')

DESCRIPTOR_LINE = Optional(GLYPH)('glyph') + DESCRIPTOR('descriptor')
NAMESPACE_DESCRIPTOR_LINE = Optional(GLYPH)('glyph') + NAMESPACE_DESCRIPTOR('namespace_descriptor')
EMPTY = Empty()

LIST_ITEM_LINE = Literal('-')('list_item_glyph')
LINE = Optional(LIST_ITEM_LINE | NAMESPACE_DESCRIPTOR_LINE | DESCRIPTOR_LINE | EMPTY('descriptor')) + Optional(COLON)

NUMBER = Word(nums)
QUOTED_STRING = QuotedString(quoteChar="'")
TRANSLATION = Suppress('!') + DESCRIPTOR('language_code')
PROPERTY_ACCESSOR = Suppress('.') + Word(alphanums + '_')
META_ACCESSOR = Suppress('@') + Word(alphanums + '_')
TRANSLATION_ACCESSOR = Suppress('!') + DESCRIPTOR('translation_descriptor') + ZeroOrMore(PROPERTY_ACCESSOR.setParseAction(named('property')))('properties')
MODEL = Literal('+')('glyph') + DESCRIPTOR('model_descriptor')
FIELD = Literal('.')('glyph') + DESCRIPTOR('field_descriptor')
COMPONENT_DESCRIPTOR = Suppress('*') + DESCRIPTOR('component_descriptor')
CONTEXT_ACCESSOR = Literal('_context')('context_accessor')
CONTEXT_ITEM = Optional('.') + DESCRIPTOR('context_item')
COMBINED_ACCESSOR = (MODEL | CONTEXT_ITEM) + OneOrMore(PROPERTY_ACCESSOR.setParseAction(named('property')) | META_ACCESSOR.setParseAction(named('meta_data')))('properties')
MOUSTACHE_EXPRESSION = CONTEXT_ACCESSOR | COMBINED_ACCESSOR | CONTEXT_ITEM | COMPONENT_DESCRIPTOR

UID = Suppress('#') + Word(alphanums, excludeChars='# : .')
CLS = Suppress('.') + Word(alphanums, excludeChars='. : #')
CLASSES = ZeroOrMore(CLS)('classes')
ID_CLASSES = Optional(UID)('uid') + CLASSES
ATTRIBUTE_KEY = Word(alphanums + '_' + '-', excludeChars=": = '")
MOUSTACHE_ATTRIBUTE_VALUE = NUMBER('number') | QUOTED_STRING('quoted_string') | MOUSTACHE_EXPRESSION
MOUSTACHE_ATTRIBUTE = ATTRIBUTE_KEY('moustache_attribute_key') + Optional(Literal('=') + MOUSTACHE_ATTRIBUTE_VALUE('moustache_attribute_value'))
MOUSTACHE_ATTRIBUTES = ZeroOrMore(Group(MOUSTACHE_ATTRIBUTE('moustache_attribute')))
# PARAM = (CONTEXT_ITEM('context_item') | CONTEXT('context')) + Optional(',')
# PARAM_LIST = ZeroOrMore(PARAM)
# FRAMEWORK_COMPONENT = Suppress('*core-') + DESCRIPTOR('framework_component') + PARAM_LIST('param_list')
FRAMEWORK_COMPONENT = Suppress('*core-') + DESCRIPTOR('framework_component') + MOUSTACHE_ATTRIBUTES('moustache_attributes')
VALUE_ACCESSOR = Literal('_value')('value_accessor')
LIST = Literal('[]')('list')
DICT = Literal('{}')('dict')
BOOLEAN = (Literal('True') or Literal('False'))('boolean')
LITERAL = (quotedString.addParseAction(removeQuotes) ^ pyparsing_common.number)('literal')
EXPRESSION = (
    BOOLEAN ^ LITERAL ^ LIST ^ DICT ^ VALUE_ACCESSOR ^ FRAMEWORK_COMPONENT
    ^ COMBINED_ACCESSOR('context_item_with_property') ^ CONTEXT_ITEM
    ^ MODEL ^ COMPONENT_DESCRIPTOR ^ ARITH_EXPRESSION('arith_expression')
    ^ TRANSLATION_ACCESSOR('translation_accessor'))
MOUSTACHE = Suppress('{')
MOUSTACHE += EXPRESSION
MOUSTACHE += Suppress('}')
ATTRIBUTE_VALUE = Optional(Literal("'") | Literal('"')) + MOUSTACHE('moustache') + Optional(Literal("'") | Literal('"')) | NUMBER('number') | QUOTED_STRING('quoted_string') | EXPRESSION
ATTRIBUTE = ATTRIBUTE_KEY('attribute_key') + Optional(Literal('=') + ATTRIBUTE_VALUE('attribute_value'))
ATTRIBUTES = ZeroOrMore(Group(ATTRIBUTE('attribute')))

INLINE_SEMANTICS_CONTENT = ZeroOrMore(UNQUOTED_WORDS.leaveWhitespace()('inline_semantic_content_words') | TRANSLATION_ACCESSOR('translation_accessor') | MOUSTACHE('moustache'))
INLINE_SEMANTICS_ELEMENT = DESCRIPTOR('descriptor') + ID_CLASSES('id_classes')
INLINE_SEMANTICS_ELEMENT += ATTRIBUTES('attributes')
INLINE_SEMANTICS_ELEMENT += Optional(COLON('colon') + Optional(' ') + INLINE_SEMANTICS_CONTENT('inline_semantics_content'))
INLINE_SEMANTICS = Suppress('<') + INLINE_SEMANTICS_ELEMENT + Optional(' ') + Suppress('>')

INLINE_CONTENT = \
    Suppress("'") + ZeroOrMore(Literal(' ')('space')
    | INLINE_SEMANTICS.setParseAction(named('inline_semantics'))
    | UNQUOTED_WORDS.setParseAction(named('inline_content_words'))
    | MOUSTACHE.setParseAction(named('moustache'))) + Suppress("'")

ELEMENT = Optional(DESCRIPTOR('descriptor')) + ID_CLASSES('id_classes')
ELEMENT += ATTRIBUTES('attributes') + Optional(COLON)('colon') + Optional(' ')
ELEMENT += Optional(INLINE_CONTENT('inline_content') | EXPRESSION('expression'))

# instruction semantics

FILENAME = DESCRIPTOR('filename')
URL = Word(printables, excludeChars='* "  = : # . { }' + "'")

INHERIT = Suppress('#') + Literal('inherit')('instruction')
INHERIT += FILENAME('templatefile')

IMPORT = Suppress('#') + Literal('import')('instruction')
IMPORT += FILENAME('templatefile')

INCLUDE = Suppress('#') + Literal('include')('instruction')
INCLUDE += FILENAME('templatefile')

NAMESPACE = Suppress('#') + Literal('namespace')('instruction')
NAMESPACE += DESCRIPTOR('namespace') + '=' + URL

INSTRUCTION = INHERIT | IMPORT | INCLUDE | NAMESPACE


# route semantics
url_chars = alphanums + '-_.~%+'
PATH_SEGMENT = Word(url_chars)
PATH_VARIABLE = Suppress('{') + DESCRIPTOR('variable_descriptor') + Suppress('}')
PATH_ITEM = Suppress(Optional('/'))('leading_slash') + (PATH_SEGMENT.setParseAction(named('path_segment'))
                         | PATH_VARIABLE.setParseAction(named('path_variable')))
PATH_ITEMS = ZeroOrMore(PATH_ITEM('path_item'))
ROUTE_PATH = PATH_ITEMS('path_items')
ROUTE_PATH += Optional('/')('trailing_slash')
ROUTE = DESCRIPTOR('descriptor') + COLON + Optional(' ') + Suppress("'") + ROUTE_PATH('route_path') + Suppress("'")


# code semantics

SOMETHING = Suppress('%') + Word(printables + ' ')('some_thing')
ITERATOR = COMBINED_ACCESSOR | CONTEXT_ITEM
IF_STATEMENT = Suppress('%') + Suppress('if') + EXPRESSION('expression') + Suppress(':')
FOR_LOOP = Suppress('%') + Suppress('for') + DESCRIPTOR('variable') + Suppress('in')
FOR_LOOP += ITERATOR('iterator') + Suppress(':')
CODE = IF_STATEMENT('if_statement') | FOR_LOOP('for_loop') | SOMETHING('some_thing')

COMPONENT_CALL = DESCRIPTOR('namespace') - Suppress('-') - DESCRIPTOR('component_descriptor') + ATTRIBUTES('attributes')
COMPONENT_CALL += Optional(COLON)('colon') + Optional(' ') + Optional(INLINE_CONTENT('inline_content') | EXPRESSION('expression'))

# list items
LIST_ITEM = Literal('-')('list_item_glyph') + Optional(INLINE_CONTENT)

ASSIGNMENT_VALUE = Optional(EXPRESSION('expression') | INLINE_CONTENT('inline_content'))
ASSIGNMENT = Optional(GLYPH) + DESCRIPTOR('descriptor') + COLON('colon') + Optional(' ') + ASSIGNMENT_VALUE('assignment_value')
