import abc
from typing import TypeVar, Optional

from ..ast import (
    QueryRow, QueryOperationStatement, QueryAggregationStatement, QueryChangeStatement,
    QueryBuildException, QueryUpdateStatement, AggregationType
)
from .base import AbstractOperationQueryParser

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['BaseOperationQueryParser']

T = TypeVar('T')


class BaseOperationQueryParser(AbstractOperationQueryParser[T]):

    @abc.abstractmethod
    def process_aggregation_statement(
            self, db_query: T, aggregation_type: AggregationType,
            row: Optional[QueryRow]) -> T:
        pass

    @abc.abstractmethod
    def process_change_statement(self, db_query: T, change_statement: QueryChangeStatement) -> T:
        pass

    @abc.abstractmethod
    def process_update_statement(self, db_query: T, update_statement: QueryUpdateStatement) -> T:
        pass

    def parse_query(self, db_query: T, query: QueryOperationStatement) -> T:
        if isinstance(query, QueryAggregationStatement):
            return self.process_aggregation_statement(db_query, query.aggregation, query.row)
        if isinstance(query, QueryChangeStatement):
            return self.process_change_statement(db_query, query)
        if isinstance(query, QueryUpdateStatement):
            return self.process_update_statement(db_query, query)
        raise QueryBuildException("Cannot parse %s" % query)
