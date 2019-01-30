import abc
from typing import Type, TypeVar, Generic, TYPE_CHECKING, Optional

from ..ast import (
    QueryFilterStatement, QueryAst, QueryOperationStatement, QueryTransformationStatement,
    QueryBuildException
)

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'AbstractQueryParser', 'BaseQueryParser', 'AbstractFilterQueryParser',
    'AbstractTransformationQueryParser', 'AbstractOperationQueryParser'
]

T = TypeVar('T')


class AbstractQueryParser(Generic[T]):

    @abc.abstractmethod
    def parse_query(self, query: QueryAst) -> T:
        pass


class AbstractFilterQueryParser(Generic[T]):

    @abc.abstractmethod
    def parse_query(self, query: QueryFilterStatement, initial_query: T) -> T:
        pass


class AbstractTransformationQueryParser(Generic[T]):

    @abc.abstractmethod
    def parse_query(self, db_query: T, query: QueryTransformationStatement) -> T:
        pass


class AbstractOperationQueryParser(Generic[T]):

    @abc.abstractmethod
    def parse_query(self, db_query: T, query: QueryOperationStatement) -> T:
        pass


class BaseQueryParser(AbstractQueryParser[T]):

    __filter_parser__: Type[AbstractFilterQueryParser[T]]
    __transformation_parser__: Type[AbstractTransformationQueryParser[T]]
    __operation_parser__: Type[AbstractOperationQueryParser[T]]

    def __init__(self):
        self.filter_parser = self.__filter_parser__()
        self.transformation_parser = self.__transformation_parser__()
        self.operation_parser = self.__operation_parser__()

    def pre_processing(self, query: QueryAst) -> QueryAst:  # pylint: disable=no-self-use
        return query

    def post_processing(self, db_query: T, model_class: Type['Model']):  # pylint: disable=no-self-use,unused-argument
        return db_query

    @abc.abstractmethod
    def initial_query(self, model_class: Type['Model'], query: QueryAst) -> T:
        pass

    def _flow_query_parsing(self, query: QueryAst, initial_query: T, model_class: Type['Model']) -> T:
        from anji_orm.core.model import ModelType

        if isinstance(query, QueryFilterStatement):
            if model_class._model_type == ModelType.child:  # type: ignore
                child_subquery = model_class._python_info.eq(
                    f'{model_class.__module__}.{model_class.__name__}'
                )
                query = query & child_subquery
                query._adapt_query()
            return self.filter_parser.parse_query(query, initial_query)
        if isinstance(query, QueryTransformationStatement):
            return self.transformation_parser.parse_query(
                self._flow_query_parsing(query.base_query, initial_query, model_class),
                query
            )
        if isinstance(query, QueryOperationStatement):
            return self.operation_parser.parse_query(
                self._flow_query_parsing(query.base_query, initial_query, model_class),
                query
            )
        raise QueryBuildException("Unknown query type!")

    def parse_query(self, query: QueryAst) -> T:
        model_class: Optional[Type['Model']] = query.model_ref
        if model_class is None:
            raise QueryBuildException("Cannot parse query without model ref")
        query = self.pre_processing(query)
        initial_query = self.initial_query(model_class, query)
        db_query = self._flow_query_parsing(query, initial_query, model_class)
        return self.post_processing(db_query, model_class)
