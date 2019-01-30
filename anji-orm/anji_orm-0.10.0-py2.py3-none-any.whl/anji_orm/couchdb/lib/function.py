import abc
from typing import Optional, Dict, List

try:
    import ujson as json
except ImportError:
    import json  # type: ignore

from ...core import (
    AggregationType, QueryRow, QueryBinaryFilterStatement,
    StatementType, Interval
)

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    "CouchDBFilterMapFunction", "CouchDBReduceFunction", "CouchDBFunction",
    "CouchDBFilterFunction", 'CouchDBUpdateFunction'
]

SELECTOR_STATEMENT_MAPPING = {
    "$eq": "===",
    "$ne": "!==",
    "$lte": "<=",
    "$gte": ">=",
    "$lt": "<",
    "$gt": ">"
}


def convert_attribute(attribute):
    if isinstance(attribute, QueryRow):
        row_path = map(lambda x: f"['{x}']", attribute.row_path)
        return f"doc{''.join(row_path)}"
    return attribute


def convert_value(value):
    if isinstance(value, str) and not value.startswith('doc['):
        return f"'{value}'"
    return value


class CouchDBFunction(abc.ABC):

    __slots__ = ()

    @abc.abstractmethod
    def to_javascript(self) -> Optional[str]:
        pass


class CouchDBFilterMapFunction(CouchDBFunction):

    __slots__ = ('_emit_key_field', '_emit_doc', 'conditions')

    def __init__(self, db_query_selector: Dict, row: Optional[QueryRow] = None) -> None:
        self.conditions: List[str] = []
        self.add_parsed(db_query_selector)
        self._emit_key_field = 'doc._id'
        self._emit_doc = 'doc'
        self.set_emit_doc(row)

    @property
    def emit(self) -> str:
        return f"emit({self._emit_key_field}, {self._emit_doc});"

    def set_emit_doc(self, value: Optional[QueryRow]) -> None:
        if value:
            self._emit_doc = convert_attribute(value)
        else:
            self._emit_doc = 'doc'

    def set_emit_key_field(self, value: QueryRow) -> None:
        self._emit_key_field = f'doc.{value.row_name}'

    emit_row = property(None, set_emit_doc)
    emit_key_field = property(None, set_emit_key_field)

    def to_javascript(self) -> str:
        function_lines = ['function (doc){']
        if self.conditions:
            selection_filter = ' && '.join(self.conditions)
            function_lines.append(f"if ({selection_filter}) {'{'}")
            function_lines.append(self.emit)
            function_lines.append("}")
        else:
            function_lines.append(self.emit)
        function_lines.append('}')
        return '\n'.join(function_lines)

    def add_parsed(self, db_query_selector: Dict) -> None:
        for key, selector_conditinios in db_query_selector.items():
            if key == '_id' and selector_conditinios == {'$gt': None}:
                continue
            for condition_key, condition_value in selector_conditinios.items():
                if condition_key == '$in':
                    self.conditions.append(f"{str(condition_value)}.includes(doc['{key}'])")
                elif condition_key == '$regex':
                    self.conditions.append(f"/{str(condition_value)}/.test(doc['{key}'])")
                else:
                    self.conditions.append(
                        f"doc['{key}'] {SELECTOR_STATEMENT_MAPPING[condition_key]}"
                        f" {convert_value(condition_value)}"
                    )

    def add(self, query: QueryBinaryFilterStatement) -> None:
        left = convert_attribute(query.left)
        right = convert_value(convert_attribute(query.right))
        if query.statement_type == StatementType.bound:
            interval: Interval = right
            left_operation = '>=' if interval.left_close else '>'
            right_operation = '<=' if interval.right_close else '<'
            self.conditions.append(f"{left} {left_operation} {interval.left_bound}")
            self.conditions.append(f"{left} {right_operation} {interval.right_bound}")
        elif query.statement_type == StatementType.isin:
            self.conditions.append(f"{right}.includes({left})")
        elif query.statement_type == StatementType.match:
            self.conditions.append(f"/{str(right)}/.test({left})")
        else:
            self.conditions.append(
                f"{left} {query.statement_type.value} {right}"
            )

    def __eq__(self, other) -> bool:
        if not isinstance(self, CouchDBFilterMapFunction):
            return False
        return (
            self.conditions == other.conditions and
            self._emit_doc == other._emit_doc and
            self._emit_key_field == other._emit_key_field
        )


class CouchDBReduceFunction(CouchDBFunction):

    __slots__ = ('type', )

    def __init__(self, aggregation_type: AggregationType) -> None:
        self.type = aggregation_type

    def to_javascript(self) -> str:
        if self.type in (AggregationType.sum, AggregationType.count):
            return f"_{self.type.name}"
        if self.type in (AggregationType.min, AggregationType.max):
            comparation_operator = '>' if self.type == AggregationType.max else '<'
            return (
                "function (keys, values) {\n"
                "return values.reduce(function (p, v) {\n"
                f"return (p {comparation_operator} v ? p : v);\n"
                "});"
                '}'
            )
        return (
            "function (keys, values) {\n"
            "return sum(values) / values.lenght"
            '}'
        )

    def __eq__(self, other) -> bool:
        if not isinstance(self, CouchDBReduceFunction):
            return False
        return self.type == other.type


class CouchDBFilterFunction(CouchDBFunction):

    _slots__ = ('filter_map', )

    def __init__(self, filter_map: CouchDBFilterMapFunction) -> None:
        self.filter_map = filter_map

    def to_javascript(self) -> Optional[str]:
        function_lines = ['function(doc, req) {']
        if self.filter_map.conditions:
            selection_filter = ' && '.join(self.filter_map.conditions)
            function_lines.append(f"if ({selection_filter}) {'{'}")
            function_lines.append('return true;')
            function_lines.append("}")
        function_lines.append('return false;')
        function_lines.append('}')
        return ' '.join(function_lines)

    def __eq__(self, other) -> bool:
        if not isinstance(self, CouchDBFilterFunction):
            return False
        return self.filter_map == other.filter_map


class CouchDBUpdateFunction(CouchDBFunction):

    __slots__ = ('update_dict', 'filter_map')

    def __init__(self, update_dict: Dict, filter_map: Optional[CouchDBFilterMapFunction]) -> None:
        self.filter_map = filter_map
        self.update_dict = update_dict

    def to_javascript(self) -> Optional[str]:
        function_lines = ['function(doc, req) {']
        update_lines = [
            f'var update_dict = {json.dumps(self.update_dict)};',
            """
            var mergeFunction = function(target, source) {
                for (var key in source) {
                    if (source.hasOwnProperty(key)) {
                        target[key] = source[key];
                    }
                }
                return target;
            };
            """,
            'doc = mergeFunction(doc, update_dict);'
        ]
        if self.filter_map and self.filter_map.conditions:
            selection_filter = ' && '.join(self.filter_map.conditions)
            function_lines.append(f"if ({selection_filter}) {'{'}")
            function_lines.extend(update_lines)
            function_lines.append('return [doc, "Document updated"];')
            function_lines.append("}")
            function_lines.append('return [null, "Document ignored"];')
            function_lines.append('}')
        else:
            function_lines.extend(update_lines)
            function_lines.append('return [doc, "Document updated"];')
            function_lines.append("}")
        return ' '.join(function_lines)

    def __eq__(self, other) -> bool:
        if not isinstance(self, CouchDBUpdateFunction):
            return False
        return self.filter_map == other.filter_map and self.update_dict == other.update_dict
