# pylint: disable=no-self-use
from typing import Optional
import operator

import rethinkdb as R

from ...core import (
    QueryRow, BaseOperationQueryParser, AggregationType, QueryBuildException,
    QueryChangeStatement, QueryUpdateStatement, QueryFilterStatement
)

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['RethinkDBOperationQueryParser']


class RethinkDBOperationQueryParser(BaseOperationQueryParser[R.RqlQuery]):

    def process_aggregation_statement(
            self, db_query: R.RqlQuery, aggregation_type: AggregationType,
            row: Optional[QueryRow]) -> R.RqlQuery:
        if aggregation_type == AggregationType.count:
            return db_query.count()
        if row is None:
            raise QueryBuildException(f"Cannot process {aggregation_type} without row")
        for row_name in row.row_path:
            db_query = db_query.get_field(row_name)
        return getattr(db_query, aggregation_type.name)()

    def process_change_statement(self, db_query: R.RqlQuery, change_statement: QueryChangeStatement) -> R.RqlQuery:
        return db_query.changes(
            include_initial=change_statement.with_initial,
            include_types=change_statement.with_types
        )

    def process_update_statement(self, db_query: R.RqlQuery, update_statement: QueryUpdateStatement) -> R.RqlQuery:
        if update_statement.atomic:
            initial_query = update_statement.base_query
            while not isinstance(initial_query, QueryFilterStatement):
                initial_query = initial_query.base_query  # type: ignore
            return db_query.update(
                lambda record:
                R.branch(
                    initial_query.to_python(record, operator.getitem),
                    update_statement.update_dict,
                    None
                )
            )
        return db_query.update(update_statement.update_dict)
