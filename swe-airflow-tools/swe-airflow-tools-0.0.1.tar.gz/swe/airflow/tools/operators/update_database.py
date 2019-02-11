# -*- coding: utf-8 -*-

import logging

from airflow.hooks.dbapi_hook import DbApiHook
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

from .abstract_operator import AbstractOperator

from ..hooks.postgres_hook import PostgresHook

from ..storage import IStorage


class UpdateDatabaseOperator(AbstractOperator):
    """
    Executes sql code in a specific Postgres database
    :param postgres_conn_id: reference to a specific postgres database
    :type postgres_conn_id: string
    :param sql: the sql code to be executed
    :type sql: Can receive a str representing a sql statement,
        a list of str (sql statements), or reference to a template file.
        Template reference are recognized by str ending in '.sql'
    """

    template_fields = ('storage_reference', )
    #template_ext = ('.sql',)
    ui_color = '#ededed'

    @apply_defaults
    def __init__(self,
                 conn_id,
                 database,
                 table_name,
                 hook,
                 rows=None,
                 primary_key=None,
                 *args,
                 **kwargs):

        super(UpdateDatabaseOperator, self).__init__(*args, **kwargs)

        if not database:
            raise AirflowException('Database not set!')
        if not conn_id:
            raise AirflowException('Connection ID not set!')
        if not table_name:
            raise AirflowException('Table name not set!')
        if not primary_key:
            raise AirflowException('Primary Key not set!')
        if not isinstance(hook, DbApiHook):
            raise AirflowException('Hook not set!')

        self.database = database
        self.table_name = table_name
        self.primary_key = primary_key
        self.rows = rows
        self.conn_id = conn_id
        self.hook = hook


    def _execute(self, context):
        logging.info('Executing update in {} database {} table... '.format(self.database, self.table_name))
        self.hook.update_row(self.table_name, self.rows, self.primary_key)


class PostgresUpdateDatabaseFromStorageOperator(UpdateDatabaseOperator):

    def __init__(self,
                 storage,
                 storage_reference,
                 conn_id,
                 database,
                 table_name,
                 primary_key='id',
                 *args,
                 **kwargs):

        super(PostgresUpdateDatabaseFromStorageOperator, self).__init__(
            conn_id=conn_id,
            database=database,
            table_name=table_name,
            hook=PostgresHook(postgres_conn_id=conn_id, schema=database),
            primary_key=primary_key,
            *args,
            **kwargs
        )

        if not isinstance(storage, IStorage):
            raise AirflowException('Storage object have been IStorage Type!')

        self.storage = storage
        self.storage_reference = storage_reference

    def _pre_execute(self, context):
        super()._pre_execute(context)
        self.storage.storage_reference = self.storage_reference
        self.rows = self.storage.rows
