# -*- coding: utf8 -*-
import json
import six
from .luqum.tree import OrOperation, Word, Item, Phrase, SearchField, UnknownOperation
from .luqum.utils import LuceneTreeVisitorV2, UnknownOperationResolver, LuceneTreeTransformer
from .luqum.parser import parser, lexer, ParseError
import pyparsing as pp


class ParseApplicationException(ParseError):
    pass


def process_vals(t, l):
    res = []
    for val in t:
        res.append(l(val))

    return res


def convert_number(t):
    def int_or_float(val):
        if '.' in val:
            return float(val)

        return int(val)

    return process_vals(t, int_or_float)


def convert_boolean(t):
    def bools(val):
        if val.lower() in ['true', 'yes']:
            return True

        return False

    return process_vals(t, bools)


def parse_expr(expr_text):
    operator = pp.Regex(">=|<=|!=|>|<|=")('operator')

    point = pp.Literal('.')
    e = pp.CaselessLiteral('E')
    plus_or_minus = pp.Literal('+') | pp.Literal('-')
    number = pp.Word(pp.nums)
    integer = pp.Combine(pp.Optional(plus_or_minus) + number)
    float_number = pp.Combine(integer + pp.Optional(point + pp.Optional(number)) + pp.Optional(e + integer) + pp.stringEnd)

    float_number.setParseAction(convert_number)

    TRUE = pp.Keyword("True", caseless=True) | pp.Keyword("Yes", caseless=True)
    FALSE = pp.Keyword("False", caseless=True) | pp.Keyword("No", caseless=True)

    boolean = (TRUE | FALSE)("boolean")
    boolean.setParseAction(convert_boolean)
    identifier = ~float_number + pp.Word(pp.alphanums + "_" + "." + "-" + "*" + '?')

    quoted_string = pp.QuotedString('"')
    text_identifier = (quoted_string | identifier)
    comparison_term = boolean | text_identifier | float_number
    values = pp.OneOrMore(comparison_term)('values')
    range_op = pp.Suppress(pp.CaselessLiteral('TO'))
    range_operator = (pp.Suppress('[') + comparison_term + range_op + comparison_term + pp.Suppress(']'))('range')
    range_inclusive = (pp.Suppress('{') + comparison_term + range_op + comparison_term + pp.Suppress('}'))('range_inclusive')

    condition_group = pp.Group((range_inclusive | range_operator | values | (operator + values)))('condition_group')
    conditions = pp.Group(condition_group)('conditions')

    expr = pp.infixNotation(conditions, [
        ("AND", 2, pp.opAssoc.LEFT,),
        ("OR", 2, pp.opAssoc.LEFT,),
    ])

    return expr.parseString(expr_text)


def __conditions_expr_to_sql_where(field_name, item):
    return '({sql})'.format(sql=expr_to_sql_where(field_name, item))


def quotes_if_needed(val):
    return '"%s"' % val if isinstance(val, six.string_types) else val


def __is_expr_wildcards(operator, val):
    return operator == '=' and isinstance(val, six.string_types) and ('?' in val or '*' in val)


def __convert_wildcards_to_regex(val):
    return '^' + val.replace('*', '.*').replace('?', '.') + '$'


def __condition_group_expr_to_sql_where_handle_values(field_name, item):
    if 'values' not in item:
        return

    values = item.get('values')
    operator = item.get('operator', '=')
    vals = []
    for val in values:
        if __is_expr_wildcards(operator, val):
            sql_where = 'REGEXP_CONTAINS(`{field_name}`, r"{val_as_regex}")'.format(
                val_as_regex=__convert_wildcards_to_regex(val), field_name=field_name)
        else:
            sql_where = '`{field_name}`{operator}{value}'.format(
                field_name=field_name, operator=operator, value=quotes_if_needed(val))

        vals.append(sql_where)

    return 'OR'.join(vals)


def __condition_group_expr_to_sql_where_handle_range(field_name, item):
    sql_format = None
    if 'range' in item:
        sql_format = '(`{field_name}`>={value1})AND(`{field_name}`<={value2})'
    elif 'range_inclusive' in item:
        sql_format = '(`{field_name}`>{value1})AND(`{field_name}`<{value2})'

    if sql_format is not None:
        return sql_format.format(field_name=field_name, value1=item[0], value2=item[1])


def __condition_group_expr_to_sql_where(field_name, item):
    for handlers in (
            __condition_group_expr_to_sql_where_handle_values,
            __condition_group_expr_to_sql_where_handle_range):
        result = handlers(field_name, item)
        if result:
            return result


def expr_to_sql_where(field_name, expr):
    sql = ''
    for item in expr:
        if item.getName() == 'conditions':
            sql += __conditions_expr_to_sql_where(field_name, item)
        elif item.getName() == 'condition_group':
            sql += __condition_group_expr_to_sql_where(field_name, item)

    return sql


class QueryFunction(Item):
    def __init__(self, name, node):
        self.name = name
        self.node = node

    def __str__(self):
        return str(self.node)

    @classmethod
    def create_with_args(cls, vals):
        name = cls.__name__.replace('Function', '').lower()
        node = SearchField('@' + name, vals)
        return cls(name, node)


class FunctionVersion(QueryFunction):
    def __init__(self, name, node):
        super(FunctionVersion, self).__init__(name, node)
        self.version = str(node.expr)


class FunctionPhase(QueryFunction):
    def __init__(self, name, node):
        super(FunctionPhase, self).__init__(name, node)
        self.phase = str(node.expr)


class FunctionSplit(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSplit, self).__init__(name, node)

        self.split_field = None
        self.split = {}

        split_vars = self.__validate_split_params(node)

        try:
            split_vars = list(map(float, split_vars))
            split_vars += [None] * (3 - len(split_vars))

            self.split = dict(zip(('train', 'test', 'validation'), split_vars))
        except ValueError:
            if len(split_vars) == 1:
                self.split_field = split_vars[0]
            else:
                raise ParseApplicationException('invalid values in @split')

    @classmethod
    def __validate_split_params(cls, node):
        split_vars = str(node)
        split_vars = split_vars.split(':')

        if len(split_vars) > 4:
            raise ParseApplicationException('too many values in @split')

        if len(split_vars) == 1:
            raise ParseApplicationException('@split needs at least one value')

        return split_vars[1:]


class FunctionSample(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSample, self).__init__(name, node)
        self.sample = float(node.expr.value)


class FunctionSeed(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSeed, self).__init__(name, node)
        self.seed = int(str(node.expr))


class FunctionGroupBy(QueryFunction):
    def __init__(self, name, node):
        super(FunctionGroupBy, self).__init__(name, node)
        self.group = str(node.expr)


class FunctionDatapointBy(QueryFunction):
    def __init__(self, name, node):
        super(FunctionDatapointBy, self).__init__(name, node)
        self.datapoint = str(node.expr)


FunctionGroup = FunctionGroupBy


class FunctionLimit(QueryFunction):
    def __init__(self, name, node):
        super(FunctionLimit, self).__init__(name, node)
        self.limit = int(str(node.expr))


class FunctionOffset(QueryFunction):
    def __init__(self, name, node):
        super(FunctionOffset, self).__init__(name, node)
        self.offset = int(str(node.expr))


class FunctionPath(QueryFunction):
    def __init__(self, name, node):
        super(FunctionPath, self).__init__(name, node)
        self.expr = str(node.expr)


class FunctionSize(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSize, self).__init__(name, node)
        self.expr = str(node.expr)


class MLQueryMixin(object):
    @classmethod
    def _handle_internal_function(cls, node):
        if node.name.startswith('@'):
            func_name = node.name[1:]
            func_class_name = 'Function%s' % func_name.title()
            func_class_name = func_class_name.replace('_', '')
            function_class = globals().get(func_class_name)

            if function_class is None:
                raise ParseApplicationException('invalid function %s' % func_name)

            return function_class(func_name, node)

        return None


# noinspection PyClassicStyleClass
class MLQueryTransformer(LuceneTreeTransformer, MLQueryMixin):
    def visit_search_field(self, node, parents):
        return self._handle_internal_function(node) or node

    def __call__(self, tree):
        return self.visit(tree)


class MLQueryVisitor(LuceneTreeVisitorV2):
    def __visit_binary_operation(self, node, parents, context, op):
        new_context = {}
        if context is not None:
            new_context.update(context)

        new_context['op'] = op
        for child in node.children:
            self.visit(child, context=new_context)

    def visit_and_operation(self, node, parents=None, context=None):
        self.__visit_binary_operation(node, parents, context, 'AND')

    def visit_or_operation(self, node, parents=None, context=None):
        self.__visit_binary_operation(node, parents, context, 'OR')


# noinspection PyClassicStyleClass
class VersionVisitor(MLQueryVisitor):
    def __init__(self):
        self.version = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_version(self, node, parents=None, context=None):
        self.version = node.version


# noinspection PyClassicStyleClass
class SQLQueryBuilder(MLQueryVisitor, MLQueryMixin):
    phase_where_level = -1
    random_function_level = -1

    def __init__(self, sql_helper):
        self.__where = {}
        self.__limit = []
        self.__vars = {}
        self.__has_complex_data = False
        self.__sql_helper = sql_helper

    internal_function_names = ['sample', 'seed', 'group', 'group_by', 'datapoint_by', 'offset', 'version', 'limit', 'path', 'size']

    @property
    def has_complex_data(self):
        return self.__has_complex_data

    def visit_function_sample(self, node, parents=None, context=None):
        sample_percentile = 1.0 - node.sample

        self.__where.setdefault(self.random_function_level, []).append(
            ('AND', '($random_function>{sample_percentile:.4g})'.format(sample_percentile=sample_percentile)))

        self.__vars['sample_percentile'] = sample_percentile
        self.__vars['sample'] = node.sample

    def visit_function_path(self, node, parents=None, context=None):
        context = context or {}
        self.__add_where('_sha', node.expr, context.get('op'))

    def visit_function_size(self, node, parents=None, context=None):
        context = context or {}
        self.__add_where('_size', node.expr, context.get('op'))

    def visit_function_seed(self, node, parents=None, context=None):
        self.__vars['seed'] = node.seed

    def visit_function_limit(self, node, parents=None, context=None):
        self.__vars['limit'] = node.limit

    def visit_function_offset(self, node, parents=None, context=None):
        self.__vars['offset'] = node.offset

    def visit_function_group(self, node, parents=None, context=None):
        self.visit_function_group_by(node, parents, context)

    def visit_function_group_by(self, node, parents=None, context=None):
        self.__vars['group'] = node.group

    def visit_function_datapoint_by(self, node, parents=None, context=None):
        self.__vars['datapoint'] = node.datapoint

    def visit_function_split(self, node, parents=None, context=None):
        if node.split_field is not None:
            self.__vars['split_field'] = node.split_field
        else:
            self.__vars.update(get_split_vars(node.split))

    def visit_function_phase(self, node, parents=None, context=None):
        self.__add_where('_phase', node.phase, 'AND', level=self.phase_where_level)

    def visit_function_version(self, node, parents=None, context=None):
        self.__vars['version'] = node.version

    def visit_func_limit(self, node, parents=None, context=None):
        self.__vars['limit'] = node.limit

    def visit_group(self, node, parents=None, context=None):
        self._sub_visit(node.expr, context=context, on_sql=self.wrap_in_parentheses)

    def visit_not(self, node, parents=None, context=None):
        def wrap_in_not(sql):
            return '(NOT ' + self.wrap_in_parentheses(sql) + ')'

        self._sub_visit(node.a, context=context, on_sql=wrap_in_not)

    def visit_prohibit(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_phrase(self, node, parents=None, context=None):
        phrase = str(node)

        phrase = phrase.strip()

        self.__add_where(context.get('field_name'), phrase, context.get('op'))

    def visit_range(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_plus(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node)[1:], context.get('op'))

    def visit_field_group(self, node, parents=None, context=None):
        self.visit(node.expr, parents + [node], context)

    def __add_standalone_where(self, where, op, level=0):
        self.__where.setdefault(level, []).append((op, where))

    def __add_where(self, field_name, expr, op, level=0):
        if expr is None:
            self.__where.setdefault(level, []).append((None, '%s is NULL' % field_name))
            return

        where = expr_to_sql_where(field_name, parse_expr(expr))
        self.__add_standalone_where(where, op, level)

    def visit_word(self, node, parents=None, context=None):
        if context is None:
            raise ParseApplicationException('invalid field %s' % node)

        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def _handle_complex_field(self, name, value, op):
        parts = name.split('.')

        fields = '.'.join(parts[1:])
        first_part = parts[0]

        def validate_value():
            if value.isdigit():
                return int(value)

            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]

            if value.endswith("'"):
                return value[:-1]

            return value

        value = json.dumps(validate_value())

        sql = '(matchJson(`{first_part}`, "{fields}", {value}))'.format(
            first_part=first_part,
            fields=fields,
            value=value)

        self.__has_complex_data = True
        self.__add_standalone_where(sql, op)

    @classmethod
    def _is_complex_field(cls, name):
        return '.' in name

    def visit_search_field(self, node, parents=None, context=None):
        function_node = self._handle_internal_function(node)
        if function_node is not None:
            return function_node

        context = context or {}

        for child in node.children:
            if isinstance(child, (Word, Phrase)):
                value = str(node.expr)
                if value.lower() == 'null':
                    self.__add_where(node.name, None, 'is')
                elif self._is_complex_field(node.name):
                    self._handle_complex_field(node.name, value, context.get('op'))
                else:
                    self.__add_where(node.name, value, context.get('op'))
            else:
                sub_context = {}
                sub_context.update(context)
                sub_context['field_name'] = node.name
                self._sub_visit(node.expr, context=sub_context)

    @classmethod
    def __combine_where(cls, sql_builder):
        combine_where = {}
        for bucket, wheres in sorted(sql_builder.where.items()):
            for where in wheres:
                operator, expr = where

                combine_where.setdefault(bucket, []).append((operator, expr))

        return combine_where

    def _sub_visit(self, child, context=None, on_sql=None):
        sql_builder = SQLQueryBuilder(self.__sql_helper)
        sql_builder.visit(child, context=context)

        self.__vars.update(sql_builder.vars)

        combine_where = self.__combine_where(sql_builder)

        for bucket, wheres in combine_where.items():
            op = None
            sql = ''
            for where in wheres:
                operator, expr = where
                if op is not None:
                    sql += op

                sql += expr
                op = operator

            if on_sql:
                sql = on_sql(sql)
            elif len(wheres) > 1:
                sql = self.wrap_in_parentheses(sql)

            op = (context or {}).get('op')
            self.__where.setdefault(bucket, []).append((op, sql))

    @classmethod
    def wrap_in_parentheses(cls, text):
        return '(%s)' % text

    def build_vars(self):
        if not self.__vars:
            return None

        return self.__vars

    def __build_where(self):
        sql = ''
        last_operator = None
        combine_operator = ''
        for bucket, wheres in sorted(self.__where.items()):
            group_where = ''
            for where in wheres:
                operator, expr = where

                if group_where:
                    group_where += last_operator if operator is None else operator

                group_where += expr

                last_operator = operator

            if len(wheres) > 1:
                group_where = self.wrap_in_parentheses(group_where)

            sql = sql + combine_operator + group_where
            combine_operator = last_operator

        return sql

    def build_where(self):
        return self.__build_where() or None  # Make sure to return None and not empty string

    @property
    def where(self):
        return self.__where

    @property
    def vars(self):
        return self.__vars


# noinspection PyClassicStyleClass
class AddLimitOffsetFunctionTransformer(LuceneTreeTransformer):
    def __init__(self, limit, offset):
        self.__offset_function = FunctionOffset.create_with_args(offset) if offset is not None else None
        self.__limit_function = FunctionLimit.create_with_args(limit) if limit is not None else None
        self.__has_offset = False
        self.__has_limit = False

    # noinspection PyUnusedLocal
    def visit_function_offset(self, node, parents=None, context=None):
        self.__has_offset = True
        return self.__offset_function or node

    # noinspection PyUnusedLocal
    def visit_function_limit(self, node, parents=None, context=None):
        self.__has_limit = True
        return self.__limit_function or node

    def __call__(self, tree):
        result = self.visit(tree)
        if not self.__has_offset and self.__offset_function is not None:
            result = UnknownOperation(self.__offset_function, result)

        if not self.__has_limit and self.__limit_function is not None:
            result = UnknownOperation(self.__limit_function, result)

        return result


def get_split_vars(split):
    sql_vars = {}

    start = 0.
    for phase in ['train', 'test', 'validation']:
        percentage = split.get(phase)
        if phase is None:
            continue

        if percentage is None:
            sql_vars['phase_%s_start' % phase] = -1
            sql_vars['phase_%s_end' % phase] = -1
            continue

        sql_vars['phase_%s_start' % phase] = start
        sql_vars['phase_%s_end' % phase] = start + percentage

        start += percentage

    return sql_vars


class QueryParser(object):
    def __init__(self):
        self.__parser = parser()

    def parse_query(self, query):
        return self.__parser.parse(query, lexer=lexer())


class QueryUtils(object):
    @classmethod
    def run_visitor_on_query_text(cls, query_text, visitor, parser_=None):
        parser_ = parser_ or QueryParser()
        tree = parser_.parse_query(query_text)
        visit_query(visitor, tree)
        return tree, visitor

    @classmethod
    def get_version(cls, query_text, parser_=None):
        _, visitor = cls.run_visitor_on_query_text(query_text, VersionVisitor(), parser_=parser_)
        return visitor.version or 'head'


def resolve_tree(tree, *transformers):
    transformers2 = [UnknownOperationResolver(OrOperation), MLQueryTransformer()]

    transformers2.extend(transformers)

    resolved_tree = None
    for transformer in transformers2:
        if resolved_tree is None:
            resolved_tree = transformer(tree)
            continue

        resolved_tree = transformer(resolved_tree)

    return resolved_tree


def visit_query(visitor, tree):
    resolver = resolve_tree(tree)
    visitor.visit(resolver)

    return visitor


def tree_to_sql_builder(tree, sql_helper):
    sql_builder = SQLQueryBuilder(sql_helper)
    visit_query(sql_builder, tree)

    return sql_builder


def tree_to_sql_parts(tree, sql_helper):
    sql_builder = tree_to_sql_builder(tree, sql_helper)

    return sql_builder.build_vars(), sql_builder.build_where()


if __name__ == '__main__':  # pragma: no cover
    QueryParser().parse_query('(type:Annotation OR type:Image) AND (bucket:1172 or bucket:3848 or bucket:2581 or bucket:269 or bucket:802)')
