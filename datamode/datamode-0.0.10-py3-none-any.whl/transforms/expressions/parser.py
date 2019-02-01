# pylint: disable=unused-wildcard-import, wildcard-import
from distutils.util import strtobool
from pyparsing import *

# Note: if you wrap an expression in a Group, the expression will contain the named results
# below it and not let them leak through to the expression that holds the Group.

# Important:
# This makes parsing (especially using multiple layers of infixNotation) way, way faster.
# Faster meaning from completely unusably slow (without packrat) to blazing fast (with packrat), using this parser and 4-5 extra levels of infixNotation.
# Don't turn it on if any functions have side effects though.
ParserElement.enablePackrat()


# In this minilanguage, strings are required to be single-quoted, and table/column names can optionally be double-quoted to handle spaces.
# Example: "My Table"."My Column" == 'somestring'

###
### Utilities
###

# Put each of the characters into their own suppressed element
lpar, rpar, comma, period, assignment = map(Suppress, '(),.=')
dbchars = alphanums + '_'

_and = Suppress( CaselessLiteral('and') )

###
### Primitives
###
# number = Combine (Optional('-') + Word(nums + '.') ).setParseAction(lambda toks: float(toks[0]))
number = pyparsing_common.number()

# Strings are only single-quoted. Double-quotes will be interpreted as a column name.
string = Combine(QuotedString('\''))
boolean = (CaselessLiteral('true') | CaselessLiteral('false')).setParseAction(lambda toks: bool(strtobool(toks[0])) )
is_null = CaselessLiteral('is null')('is_null').setParseAction(lambda _dummy: True)  # Set .null to true when it exists.

primitive = number | boolean | string


###
### Operands
###
equalOp = Literal('==')
notEqualOp = '!='
lessThanOp = '<'
lessOrEqualThanOp =  '<='
greaterThanOp = '>'
greaterOrEqualThanOp = '>='

comparisonOp = (equalOp ^ Literal(notEqualOp) ^ Literal(lessThanOp) ^ Literal(lessOrEqualThanOp) ^ Literal(greaterThanOp) ^ Literal(greaterOrEqualThanOp))('comparisonOp')

###
### Tables/columns
###

# Matches '10abc' but not '10 abc'
numberThenDbChars = WordStart(dbchars) + number + WordEnd(dbchars)

# 'table_1' or 'column_1' or '"my column"'
# We exclude numberThenDbChars so that we don't get '10' as a subset match of '10abc'
namedEntity = Combine(NotAny(numberThenDbChars) + WordStart(dbchars) + Word(dbchars) + WordEnd(dbchars)) ^ QuotedString('"')

table = namedEntity('table')
column = namedEntity('column')

# 'table_1.column1' or '"table_1"."column 1"' etc
tableColumn = Group( table + period + column )('tableColumn')

# The user doesn't need to fully qualify columns unless they're ambiguous.
# If MV encounters an ambiguous column, it'll throw an error (outside of parsing though)
columnOrTableColumn = column ^ tableColumn


###
### Expressions
###

# E.g. 'table.a' or 5 or 'Foo' or 'true'
atom = primitive('primitive') | columnOrTableColumn


# Pseudo-grammar:
# expr = ...
# where ... can be function(...) or table.column or string or number
# or ... can be ... [(op) ... [(op) ...]]   (basic infixNotation)
# where (op) is +-*/

infix = Forward()
funcName = Word(alphas)


###
### Uncomment this section and comment out the other 'func' section to have the parser support infix operators within functions.
###
### The parser has no problem with this, but it makes the execution logic way more complex.
###

# The stuff between lpar/rpar could easily be Optional(), to support zero-arg calls,
#   e.g. myfunction().
# The stuff between lpar/rpar could also easily be a delimitedList to support multiple args,
#   e.g. myfunction(a, b, 3)
# or both of those combined, Optional(delimitedList(infix))('arg')
#
# func = Group(funcName('name') + lpar + infix + rpar)('func')


# Current function - only supports a tableColumn or func in the function
func = Forward()
funcSingleArg = Group(func | columnOrTableColumn)('funcSingleArg')
func <<= Group(funcName('name') + lpar + funcSingleArg + rpar)('func')


# PEDMAS
infix <<= infixNotation(Group(func | atom), [
  # Note: Don't use - in infixNotation because it will steal the '-' from pyparsing_common.number.
  # ('-', 1, opAssoc.RIGHT),
  ('**', 2, opAssoc.LEFT),
  (oneOf('* /'), 2, opAssoc.LEFT),
  (oneOf('+ -'), 2, opAssoc.LEFT),
])('infix')



###
### Actions
###

# Example:
# users.foo = users.bar * 2
# Note: we can't add a name to assignmentAction directly becase multipleAssignmentActions would just return one result
# (since you can apparently only have one named result per delimitedList (?) )
defaultValue = Group(Suppress( CaselessKeyword('default') ) + atom)('default')
assignmentAction = Group(Group(columnOrTableColumn)('destination') + assignment + infix + Optional(defaultValue))

# droprows from table1.column1
fromTable = Optional( CaselessKeyword('from') + table )
droprowsAction = Group( CaselessKeyword('drop rows') + fromTable)

action = Group(droprowsAction('droprowsAction') | assignmentAction('assignmentAction'))

actions = delimitedList(action)('actions')




###
### Clauses
###

#  e.g.
#    table1.column1 == table2.column2
#    table1.column1 > table2.column2


## Wheres
# e.g. 'where table.a > table.b' or 'where table.a == "something"'
# We have to use columnOrTableColumn on the left because we want the where clause to apply to each row individually,
# and allowing a atomFromSetFunc like sum(table.a) wouldn't generate multiple rows.
whereLeft = Group(atom)('left')
whereRight = Group(atom)('right')

# Examples:
# whereStandard: transactions.price > 50
# whereIsNull:   transactions.price is null
whereStandard = whereLeft + comparisonOp + whereRight
whereIsNull = whereLeft + is_null

where = Group(whereStandard | whereIsNull)
wheresClause = Suppress( CaselessKeyword('where') ) + delimitedList(where, _and)


## Joins
# e.g. join users.user_id == purchases.user_id
joinLeft = Group(tableColumn)('left')
joinRight = Group(tableColumn)('right')

join = Group(joinLeft + Suppress(equalOp) + joinRight)
joinsClause = Suppress( CaselessKeyword('join')) + delimitedList(join, _and)

groupby = Group(columnOrTableColumn)
groupbysClause = Suppress( CaselessKeyword('groupby') | CaselessKeyword('group by')) + delimitedList(groupby, comma)


###
### Base Expression passed to the parser
###

actionBase = actions('actions')
wheresBase = Optional(wheresClause)('wheresClause')
joinsBase = Optional(joinsClause)('joinsClause')
groupbysBase = Optional(groupbysClause)('groupbysClause')
baseExpr = StringStart() + actionBase + wheresBase + joinsBase + groupbysBase + StringEnd()


# Meant as a debugging tool.
# Useful for breakpoint() and clearly seeing what the input is.
# However, for quick tests, just use .runTests().
def parse_expression(_input, expr=baseExpr, print_results=True):
  results = baseExpr.parseString(_input)
  if print_results:
    print (f'Input:\n' + _input)
    print(results.dump())
  # breakpoint()
