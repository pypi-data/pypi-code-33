from typing import Optional, Type, TYPE_CHECKING

from .base import QueryAst
from .operations import QueryOperableStatement

if TYPE_CHECKING:
    from .rows import QueryRow  # pylint: disable=unused-import
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class QueryTransformationStatement(QueryOperableStatement):

    __slots__ = ('base_query',)

    def __init__(self, base_query: 'QueryTransformableStatement', model_ref: Optional[Type['Model']] = None) -> None:
        super().__init__(model_ref=model_ref)
        self.base_query = base_query

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, QueryTransformationStatement) and
            self.base_query == other.base_query
        )

    def _adapt_query(self) -> None:
        self.base_query._adapt_query()


class QueryGroupStatament(QueryTransformationStatement):

    __slots__ = ('group_row', )

    def __init__(self, base_query: 'QueryTransformableStatement', group_row: 'QueryRow', model_ref: Optional[Type['Model']] = None) -> None:
        super().__init__(base_query, model_ref=model_ref)
        self.group_row = group_row

    def __str__(self) -> str:
        return f'{str(self.base_query)}.group({str(self.group_row)})'

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and
            isinstance(other, QueryGroupStatament) and
            self.group_row._equals(other.group_row)
        )


class QueryTransformableStatement(QueryAst):

    __slots__ = ()

    def group(self, row: 'QueryRow') -> QueryGroupStatament:
        return QueryGroupStatament(self, row, model_ref=self.model_ref)
