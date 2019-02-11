# -*- coding: utf-8 -*-

import os
import logging

from airflow.hooks.dbapi_hook import DbApiHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator, XCOM_RETURN_KEY
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

from ..storage import IStorage


class ExtractDatabaseToStorageOperator(BaseOperator):
    """
    Executes sql query in a specific database and save the results

    :param conn_id: reference to a specific database
    :type conn_id: string
    :param sql: the sql code to be executed
    :type sql: Can receive a str representing a sql statement,
        a list of str (sql statements), or reference to a template file.
        Template reference are recognized by str ending in '.sql'
    :param database: name of database which overwrite defined one in connection
    :type database: string
    """

    #__slots__ = ['sql', 'database', 'conn_id', 'storage', 'hook', 'parameters']

    template_fields = ('storage_reference',)
    ui_color = '#ededed'

    @apply_defaults
    def __init__(self,
                 sql,
                 database,
                 conn_id,
                 storage,
                 storage_reference,
                 hook,
                 parameters=None,
                 *args,
                 **kwargs):

        super(ExtractDatabaseToStorageOperator, self).__init__(*args, **kwargs)

        #if not isinstance(storage, IStorage):
        #    raise AirflowException('Storage object have been IStorage Type!')
        if not database:
            raise AirflowException('Database not set!')
        if not sql:
            raise AirflowException('SQL Query not set!')
        if not conn_id:
            raise AirflowException('Connection ID not set!')
        if not isinstance(hook, DbApiHook):
            raise AirflowException('Hook not set!')

        self.sql = sql
        self.database = database
        self.conn_id = conn_id
        self.parameters = parameters
        self.storage = storage
        self.storage_reference = storage_reference
        self.hook = hook

    def execute(self, context):
        """ Execute operator logic

            Execute query in database and convert the results
            for specfied storage and file types

            param: context for current task
            type: dict

            return dict in xcom push with storage reference
        """

        self._pre_execute(context)
        self._execute(context)
        self._post_execute(context)


    def _pre_execute(self, context):
        """ Pre-execute logic. """
        if os.path.isfile(self.sql):
            with open(self.sql, 'r') as f:
                self.sql = f.read()
        if not self.sql:
            raise AirflowException('Invalid SQL: {}!'.format(self.sql))

    def _execute(self, context):
        """
        Get records from database and store data
        :return: list fo tuples
        """

        logging.info('Get records from database. SQL: {}'.format(self.sql % (self.parameters or {})))
        result = self.hook.get_records(sql=self.sql, parameters=self.parameters)

        logging.info('Write data into storage: {}'.format(self.storage_reference))
        self.storage.write(result, storage_reference=self.storage_reference)

    def _post_execute(self, context):
        """ Post execute logic. Register task result in XCOM """

        task_instance = context['task_instance']
        task_instance.xcom_push(
            key=XCOM_RETURN_KEY,
            value={'storage': {
                        self.storage.storage_name: {
                            'object': self.storage
                        }
                  }
            }
        )

class PostgresExtractDatabaseToStorageOperator(ExtractDatabaseToStorageOperator):

    def __init__(self,
                 storage,
                 storage_reference,
                 sql,
                 conn_id,
                 parameters=None,
                 database=None,
                 *args,
                 **kwargs):

        super(PostgresExtractDatabaseToStorageOperator, self).__init__(
            storage=storage,
            storage_reference=storage_reference,
            sql=sql,
            conn_id=conn_id,
            parameters=parameters,
            database=database,
            hook=PostgresHook(postgres_conn_id=conn_id, schema=database),
            *args,
            **kwargs
        )
