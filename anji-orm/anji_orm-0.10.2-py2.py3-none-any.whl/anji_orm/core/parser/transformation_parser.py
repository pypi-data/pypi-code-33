import abc
from typing import TypeVar

from ..ast import QueryRow, QueryTransformationStatement, QueryGroupStatament, QueryBuildException
from .base import AbstractTransformationQueryParser

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['BaseTransformationQueryParser']

T = TypeVar('T')


class BaseTransformationQueryParser(AbstractTransformationQueryParser[T]):

    @abc.abstractmethod
    def process_group_statement(self, db_query: T, group_row: QueryRow) -> T:
        pass

    def parse_query(self, db_query: T, query: QueryTransformationStatement) -> T:
        if isinstance(query, QueryGroupStatament):
            return self.process_group_statement(db_query, query.group_row)
        raise QueryBuildException("Cannot parse %s" % query)
