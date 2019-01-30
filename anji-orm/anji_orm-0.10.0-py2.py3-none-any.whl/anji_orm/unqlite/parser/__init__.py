import typing

from ...core import BaseQueryParser, QueryAst, Model
from .filter_parser import UnqliteFilterQueryParser
from .transformation_parser import UnqliteTransformationQueryParser
from .operation_parser import UnqliteOperationQueryParser

from .utils import UnqliteQuery

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['UnqliteQueryParser']


class UnqliteQueryParser(BaseQueryParser[UnqliteQuery]):  # pylint: disable=too-few-public-methods

    __filter_parser__ = UnqliteFilterQueryParser
    __transformation_parser__ = UnqliteTransformationQueryParser
    __operation_parser__ = UnqliteOperationQueryParser

    def initial_query(  # pylint: disable=no-self-use
            self, model_class: typing.Type[Model],
            query: QueryAst) -> UnqliteQuery:  # pylint: disable=unused-argument
        return UnqliteQuery(model_class._table)
