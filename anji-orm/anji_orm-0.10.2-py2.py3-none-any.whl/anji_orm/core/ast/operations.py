from enum import Enum, auto
from typing import Type, Optional, Dict, TYPE_CHECKING

from .base import QueryAst


if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import
    from .filters import QueryFilterStatement  # pylint: disable=unused-import
    from .transformation import QueryTransformationStatement  # pylint: disable=unused-import
    from .rows import QueryRow  # pylint: disable=unused-import


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    'AggregationType', 'QueryOperationStatement', 'QueryChangeStatement',
    'QueryUpdateStatement', 'QueryAggregationStatement', 'QueryOperableStatement', 'QueryUpdateStatement'
]


class AggregationType(Enum):

    max = auto()
    min = auto()
    sum = auto()
    avg = auto()
    count = auto()


class QueryOperationStatement(QueryAst):

    __slots__ = ('base_query', )

    def __init__(self, base_query: 'QueryOperableStatement', model_ref: Optional[Type['Model']] = None) -> None:
        super().__init__(model_ref=model_ref)
        self.base_query = base_query

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, QueryOperationStatement) and
            self.base_query == other.base_query
        )

    def _adapt_query(self) -> None:
        self.base_query._adapt_query()


class QueryChangeStatement(QueryOperationStatement):

    __slots__ = ('with_initial', 'with_types')

    def __init__(
            self, base_query, model_ref: Optional[Type['Model']] = None, with_initial: bool = False,
            with_types: bool = False,) -> None:
        super().__init__(base_query, model_ref=model_ref)
        self.with_initial = with_initial
        self.with_types = with_types

    def __str__(self) -> str:
        return f"[{self.base_query}].changes()"

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, QueryChangeStatement) and
            self.with_initial == other.with_initial and
            self.with_types == other.with_types
        )


class QueryUpdateStatement(QueryOperationStatement):

    __slots__ = ('update_dict', 'atomic')

    def __init__(
            self, base_query, update_dict: Dict, model_ref: Optional[Type['Model']] = None,
            atomic: bool = False,) -> None:
        super().__init__(base_query, model_ref=model_ref)
        self.update_dict = update_dict
        self.atomic = atomic

    def __str__(self) -> str:
        return f'[{self.base_query}].update({self.update_dict}, atomic={self.atomic})'

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, QueryUpdateStatement) and
            self.update_dict == other.update_dict and
            self.atomic == other.atomic
        )


class QueryAggregationStatement(QueryOperationStatement):

    __slots__ = ('row', 'aggregation')

    def __init__(
            self, base_query, row: Optional['QueryRow'], aggregation: AggregationType,
            model_ref: Optional[Type['Model']] = None) -> None:
        super().__init__(base_query, model_ref=model_ref)
        self.row = row
        self.aggregation = aggregation

    def __str__(self) -> str:
        return f'{str(self.aggregation)}({str(self.row)}, {str(self.base_query)})'

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, QueryAggregationStatement) and
            self.aggregation == other.aggregation and
            ((self.row is None and other.row is None) or self.row._equals(other.row))  # type: ignore
        )


class QueryOperableStatement(QueryAst):

    __slots__ = ()

    def max(self, row: 'QueryRow') -> QueryAggregationStatement:
        return QueryAggregationStatement(self, row, AggregationType.max, model_ref=self.model_ref)

    def min(self, row: 'QueryRow') -> QueryAggregationStatement:
        return QueryAggregationStatement(self, row, AggregationType.min, model_ref=self.model_ref)

    def sum(self, row: 'QueryRow') -> QueryAggregationStatement:
        return QueryAggregationStatement(self, row, AggregationType.sum, model_ref=self.model_ref)

    def avg(self, row: 'QueryRow') -> QueryAggregationStatement:
        return QueryAggregationStatement(self, row, AggregationType.avg, model_ref=self.model_ref)

    def count(self) -> QueryAggregationStatement:
        return QueryAggregationStatement(self, None, AggregationType.count, model_ref=self.model_ref)

    def changes(self, with_initial: bool = False, with_types: bool = False) -> QueryChangeStatement:
        return QueryChangeStatement(
            self, model_ref=self.model_ref, with_initial=with_initial, with_types=with_types
        )

    def update(self, update_dict: Dict, atomic: bool = False) -> QueryUpdateStatement:
        return QueryUpdateStatement(self, update_dict, model_ref=self.model_ref, atomic=atomic)
