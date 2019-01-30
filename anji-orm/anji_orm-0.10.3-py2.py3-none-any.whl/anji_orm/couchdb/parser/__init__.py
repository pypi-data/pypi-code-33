from typing import Type
from urllib.parse import quote

from ...core import BaseQueryParser, QueryAst, Model
from ..lib import AbstractCouchDBQuery, DummyCouchDBQuery
from .filter_parser import CouchDBFilterQueryParser
from .transformation_parser import CouchDBTransformationQueryParser
from .operation_parser import CouchDBOperationQueryParser

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['CouchDBQueryParser']


class CouchDBQueryParser(BaseQueryParser[AbstractCouchDBQuery]):  # pylint: disable=too-few-public-methods

    __filter_parser__ = CouchDBFilterQueryParser
    __transformation_parser__ = CouchDBTransformationQueryParser
    __operation_parser__ = CouchDBOperationQueryParser

    def initial_query(self, model_class: Type[Model], query: QueryAst) -> AbstractCouchDBQuery:  # pylint: disable=no-self-use
        # We must define query identity to work with complex query
        # that become view, but this name should be protected from url quote problems
        # so, quote query name and replace % with points to make sure, that view name
        # will be unique and allowed to use in url
        base_query = DummyCouchDBQuery(quote(str(query)).replace('%', '.'))
        base_query.table_name = model_class._table
        return base_query
