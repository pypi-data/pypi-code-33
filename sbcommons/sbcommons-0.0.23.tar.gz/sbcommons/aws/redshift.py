import psycopg2 as pg2
from sbcommons.logging.lambda_logger import get_logger

logger = get_logger(__name__)


class RedshiftClient:
    """
    Class to interact with redshift DB.
    """

    def __init__(self, host: str, port: int, db_name: str, user: str, password: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

    def __enter__(self):
        self.connection = pg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.db_name,
            user=self.user,
            password=self.password
        )
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, *_):
        self.cursor.close()
        self.connection.close()

    def kill_locks(self, table_name: str):
        """
        Method to call to kill all acquired locks on a given DB table.

        :param table_name: name of the table to kill all locks for
        """
        locks_query = f'SELECT l.pid ' \
            f'FROM pg_locks l ' \
            f'INNER JOIN pg_stat_all_tables t ON l.relation=t.relid ' \
            f'WHERE t.schemaname || \'.\' || t.relname = \'{table_name}\' ' \
            f'    AND l."granted";'
        self.cursor.execute(locks_query)
        process_ids = [row[0] for row in self.cursor.fetchall()]

        if process_ids:
            kill_lock_queries = [f'SELECT pg_terminate_backend({pid});' for pid in process_ids]
            kill_lock_query = '\n'.join(kill_lock_queries)
            self.cursor.execute(kill_lock_query)

    def load_data(self, table, s3_bucket, s3_manifest_key):
        """
        Temporary implementation for RDS copy from local terminal.
        Should be redshift COPY statement instead

        :param table: table name to load data to
        :param s3_bucket: bucket where data exists
        :param s3_manifest_key: key holding the data
        """

        staging_table = self._create_staging_table(table)
        self._load_staging_table(staging_table, s3_bucket, s3_manifest_key)
        self._deduplicate_and_insert(table, staging_table)
        self._drop_staging_table(staging_table)
        self.connection.commit()

    def get_state(self, state_table: str, key: str):
        query = f'SELECT s.last_updated ' \
            f'FROM {state_table} s ' \
            f'WHERE s.key = \'{key}\';'
        self.cursor.execute(query)
        state = self.cursor.fetchone()
        return state[0] if state else None

    def upsert_state(self, state_table: str, key: str, value: str):
        self.kill_locks(state_table)

        if self.get_state(state_table, key):
            query = f'UPDATE {state_table} ' \
                f'SET last_updated = \'{value}\' ' \
                f'WHERE key = \'{key}\';'
        else:
            query = f'INSERT INTO {state_table} VALUES (\'{key}\', TIMESTAMP \'{value}\');'

        self.cursor.execute(query)
        self.connection.commit()

    def _create_staging_table(self, table):
        staging_table = f'{table}_staging'
        self.cursor.execute(f'CREATE TABLE {staging_table} (LIKE {table});')
        return staging_table

    def _load_staging_table(self, staging_table, bucket, s3_manifest_key):
        query = f'''
        COPY {staging_table}
        FROM 's3://{bucket}/{s3_manifest_key}'
        CREDENTIALS 'aws_iam_role=arn:aws:iam::485206745971:role/RedshiftRole'
        DELIMITER '|' EMPTYASNULL GZIP MANIFEST;
        '''
        self.cursor.execute(query)

    def _deduplicate_and_insert(self, table, staging_table):
        query = f'''
        INSERT INTO {table}
        WITH deduplicated_keys AS (
            SELECT DISTINCT stg.key
            FROM {staging_table} stg
            EXCEPT
            SELECT t.key
            FROM {table} t
        ),
        one_row_per_key AS (
            SELECT
                dk.key,
                ROW_NUMBER() OVER (PARTITION BY stg.key ORDER BY stg.event_timestamp ASC) AS rank
            FROM deduplicated_keys dk
            INNER JOIN {staging_table} stg ON stg.key = dk.key
        )
        SELECT stg.*
        FROM one_row_per_key orpk
        INNER JOIN {staging_table} stg ON stg.key = orpk.key AND orpk.rank = 1;
        '''
        self.cursor.execute(query)

    def _drop_staging_table(self, staging_table):
        self.cursor.execute(f'DROP TABLE {staging_table};')
