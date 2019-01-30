# pylint: disable=no-self-use
import rethinkdb as R

from ...core import QueryRow, BaseTransformationQueryParser
from .utils import _build_row

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['RethinkDBTransformationQueryParser']


class RethinkDBTransformationQueryParser(BaseTransformationQueryParser[R.RqlQuery]):

    def process_group_statement(self, db_query: R.RqlQuery, group_row: QueryRow) -> R.RqlQuery:
        return db_query.group(_build_row(group_row))
