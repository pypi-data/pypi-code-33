# -*- coding: utf-8 -*-

import os
import logging

from airflow.hooks.dbapi_hook import DbApiHook
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

from tools.operators.abstract_operator import AbstractOperator

from tools.hooks.postgres_hook import PostgresHook


class ExecuteDatabaseOperator(AbstractOperator):
    """
    Executes sql code in a specific Postgres database
    """

    ui_color = '#ededed'

    @apply_defaults
    def __init__(self,
                 conn_id,
                 database,
                 sql,
                 hook,
                 autocommit=False,
                 parameters=False,
                 *args,
                 **kwargs):

        super(ExecuteDatabaseOperator, self).__init__(*args, **kwargs)

        if not database:
            raise AirflowException('Database not set!')
        if not conn_id:
            raise AirflowException('Connection ID not set!')
        if not sql:
            raise AirflowException('Table name not set!')
        if not isinstance(hook, DbApiHook):
            raise AirflowException('Hook not set!')

        self.database = database
        self.sql = sql
        self.conn_id = conn_id
        self.hook = hook
        self.autocommit = autocommit
        self.parameters = parameters

    def _execute(self, context):
        logging.info('Executing script in {} database... '.format(self.database))
        self.hook.run(sql=self.sql, autocommit=self.autocommit, parameters=self.parameters)


class PostgresExecuteDatabaseOperator(ExecuteDatabaseOperator):

    def __init__(self,
                 conn_id,
                 database,
                 sql,
                 autocommit=False,
                 parameters=False,
                 *args,
                 **kwargs):

        super(PostgresExecuteDatabaseOperator, self).__init__(
            conn_id=conn_id,
            database=database,
            sql=sql,
            hook=PostgresHook(postgres_conn_id=conn_id, schema=database),
            autocommit=autocommit,
            parameters=parameters,
            *args,
            **kwargs
        )

    def _pre_execute(self, context):

        super()._pre_execute(context)

        if os.path.isfile(self.sql):
            with open(self.sql, 'r') as f:
                self.sql = f.read()

        if not self.sql:
            raise AirflowException('Invalid SQL: {}!'.format(self.sql))

