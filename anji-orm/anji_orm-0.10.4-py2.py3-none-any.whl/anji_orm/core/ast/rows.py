from typing import Type, Optional, TYPE_CHECKING, Tuple


from .base import QueryAst
from .filters import (
    QueryContainsStatement, QueryEqualStatement, QueryGreaterStatement,
    QueryGreaterOrEqualStatement, QueryNotEqualStatement, QueryLowerStatement,
    QueryLowerOrEqualStatement, QueryBinaryFilterStatement, QueryAndStatement,
    QueryMatchStatement
)

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["QueryRow", "BooleanQueryRow", "DictQueryRow", "QueryRowOrderMark"]


class QueryRow(QueryAst):

    __slots__ = ('_row_name', '_secondary_index')

    __corrupted_eq_check__ = True

    def __init__(
            self, row_name: str, secondary_index: bool = False,
            model_ref: Optional[Type['Model']] = None) -> None:
        from ..register import orm_register

        super().__init__(model_ref=model_ref)
        self._row_name = orm_register.backend_adapter.row_name_serialization(row_name)
        self._secondary_index = secondary_index

    @property
    def row_name(self) -> str:
        return self._row_name

    @property
    def row_path(self) -> Tuple[str, ...]:
        return (self._row_name, )

    @property
    def secondary_index(self) -> bool:
        return self._secondary_index

    @property
    def amount(self):
        return QueryRowOrderMark(self)

    def one_of(self, *variants) -> QueryBinaryFilterStatement:
        return QueryContainsStatement(self, variants, model_ref=self.model_ref)

    def contains(self, another_row: 'QueryRow') -> QueryBinaryFilterStatement:
        return QueryContainsStatement(another_row, self, model_ref=self.model_ref)

    def match(self, other) -> QueryBinaryFilterStatement:
        return QueryMatchStatement(self, other, model_ref=self.model_ref)

    def __eq__(self, other) -> QueryBinaryFilterStatement:  # type: ignore
        return QueryEqualStatement(self, other, model_ref=self.model_ref)

    def eq(self, other) -> QueryBinaryFilterStatement:  # pylint: disable=invalid-name
        return QueryEqualStatement(self, other, model_ref=self.model_ref)

    def __ge__(self, other) -> QueryBinaryFilterStatement:
        return QueryGreaterOrEqualStatement(self, other, model_ref=self.model_ref)

    def ge(self, other) -> QueryBinaryFilterStatement:  # pylint: disable=invalid-name
        return QueryGreaterOrEqualStatement(self, other, model_ref=self.model_ref)

    def __gt__(self, other) -> QueryBinaryFilterStatement:
        return QueryGreaterStatement(self, other, model_ref=self.model_ref)

    def gt(self, other) -> QueryBinaryFilterStatement:  # pylint: disable=invalid-name
        return QueryGreaterStatement(self, other, model_ref=self.model_ref)

    def __ne__(self, other) -> QueryBinaryFilterStatement:  # type: ignore
        return QueryNotEqualStatement(self, other, model_ref=self.model_ref)

    def ne(self, other) -> QueryBinaryFilterStatement:  # pylint: disable=invalid-name
        return QueryNotEqualStatement(self, other, model_ref=self.model_ref)

    def __lt__(self, other) -> QueryBinaryFilterStatement:
        return QueryLowerStatement(self, other, model_ref=self.model_ref)

    def lt(self, other) -> QueryBinaryFilterStatement:  # pylint: disable=invalid-name
        return QueryLowerStatement(self, other, model_ref=self.model_ref)

    def __le__(self, other) -> QueryBinaryFilterStatement:
        return QueryLowerOrEqualStatement(self, other, model_ref=self.model_ref)

    def le(self, other) -> QueryBinaryFilterStatement:  # pylint: disable=invalid-name
        return QueryLowerOrEqualStatement(self, other, model_ref=self.model_ref)

    def __str__(self) -> str:
        return f"row[{self._row_name}]"

    def _equals(self, other) -> bool:
        return (
            isinstance(other, QueryRow) and
            self._row_name == other._row_name and
            self._secondary_index == other._secondary_index
        )


class QueryRowOrderMark:

    __slots__ = ('row', 'order')

    def __init__(self, query_row: QueryRow) -> None:
        self.row = query_row
        self.order = 'asc'

    @property
    def desc(self) -> 'QueryRowOrderMark':
        self.order = 'desc'
        return self

    @property
    def asc(self) -> 'QueryRowOrderMark':
        self.order = 'asc'
        return self

    @property
    def row_name(self):
        return self.row.row_name

    @property
    def row_path(self):
        return self.row.row_path

    @property
    def secondary_index(self):
        return self.row.secondary_index

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, QueryRowOrderMark) and
            self.row._equals(other.row) and
            self.order == other.order
        )


class BooleanQueryRow(QueryRow):

    __slots__ = ()

    def false(self) -> QueryBinaryFilterStatement:
        return QueryEqualStatement(self, False, model_ref=self.model_ref)

    def true(self) -> QueryBinaryFilterStatement:
        return QueryEqualStatement(self, True, model_ref=self.model_ref)

    def __invert__(self) -> QueryBinaryFilterStatement:
        return self.false()

    def implict_cast(self, target_type: Type['QueryAst']) -> Optional['QueryAst']:
        if target_type == QueryBinaryFilterStatement:
            return QueryEqualStatement(self, True, model_ref=self.model_ref)
        return None

    def __and__(self, other) -> QueryAndStatement:
        return QueryAndStatement(
            QueryEqualStatement(self, True, model_ref=self.model_ref),
            other,
            model_ref=self.model_ref
        )

    def and_(self, other) -> QueryAndStatement:
        return self.__and__(other)


class DictQueryRow(QueryRow):

    __slots__ = ('_row_path', )

    def __init__(
            self, *row_path: str, secondary_index: bool = False,
            model_ref: Optional[Type['Model']] = None) -> None:
        from ..register import orm_register

        super().__init__(row_path[0], secondary_index, model_ref=model_ref)
        self._row_path: Tuple[str, ...] = tuple(
            orm_register.backend_adapter.row_name_serialization(x) for x in row_path
        )

    @property
    def row_name(self) -> str:
        return '.'.join(self._row_path)

    @property
    def row_path(self) -> Tuple[str, ...]:
        return self._row_path

    def __getattr__(self, name) -> 'DictQueryRow':
        return DictQueryRow(*(self._row_path + (name,)), model_ref=self.model_ref)

    def __getitem__(self, name) -> 'DictQueryRow':
        return DictQueryRow(*(self._row_path + (name,)), model_ref=self.model_ref)

    def __str__(self) -> str:
        return f"row[{self.row_name}]"

    def _equals(self, other) -> bool:
        return (
            isinstance(other, DictQueryRow) and
            self._row_path == other._row_path
        )
