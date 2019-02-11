# -*- coding: utf-8 -*-

import logging

from airflow.hooks.postgres_hook import PostgresHook as AirflowPostgresHook
from airflow.exceptions import AirflowException


class PostgresHook(AirflowPostgresHook):

    def update_row(self, table, rows, primary_key=None, commit_every=0):
        """
        A generic way to update a set of tuples into a table,
        the whole set of inserts is treated as one transaction

        :param table: Name of the target table
        :type table: str
        :param rows: The rows to insert into the table
        :type rows: iterable of tuple
        :param primary_key: The name of primary key column
        :type primary_key: iterable of strings
        :param commit_every: The maximum number of rows to insert in one
            transaction. Set to 0 to insert all rows in one transaction.
        :type commit_every: int
        """

        conn = self.get_conn()

        if self.supports_autocommit:
            self.set_autocommit(conn, False)
        conn.commit()

        cur = conn.cursor()

        row_number = 0
        row_total = len(rows)
        for row in rows:
            row_number += 1

            # l = ["%s = '%s'" % (k, v) for k, v in row.iteritems()]
            if not hasattr(row, primary_key):
                raise AirflowException('Row without ID for update: {}...'.format(row))

            where = "%s = %s" % (primary_key, self._serialize_cell(getattr(row, primary_key), conn))
            values = ["%s = %s" % (field, self._serialize_cell(getattr(row, field), conn)) for field in row._fields]

            logging.info("Updating line {} of {}. {}...".format(
                    row_number,
                    row_total,
                    where
                )
            )

            cur.execute(
                "UPDATE {0} SET {1} WHERE {2};".format(
                    table,
                    ", ".join(values),
                    where
                )
            )

            if commit_every and row_number % commit_every == 0:
                conn.commit()
                logging.info("Loaded {row_number} into {table} rows so far...".format(**locals()))

        conn.commit()
        cur.close()
        conn.close()

        logging.info("Done loading. Loaded a total of {row_number} rows...".format(**locals()))
