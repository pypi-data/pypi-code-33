# pylint: disable=no-self-use

from ...core import QueryRow, BaseTransformationQueryParser
from ..lib import AbstractCouchDBQuery

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['CouchDBTransformationQueryParser']


class CouchDBTransformationQueryParser(BaseTransformationQueryParser[AbstractCouchDBQuery]):

    def process_group_statement(self, db_query: AbstractCouchDBQuery, group_row: QueryRow) -> AbstractCouchDBQuery:
        db_query = db_query.to_ddoc_view()
        db_query.ddoc_view.map_function.emit_key_field = group_row
        if db_query.params is None:
            db_query.params = {}
        db_query.params['group'] = 'true'
        return db_query
