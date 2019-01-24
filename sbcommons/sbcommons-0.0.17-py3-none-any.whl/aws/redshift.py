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

    def load_data(self, table, s3_tmp_key):
        """
        Temporary implementation for RDS copy from local terminal.
        Should be redshift COPY statement instead

        :param table: table name to load data to
        """

        staging_table = self._create_staging_table(table)
        self._load_staging_table(staging_table, s3_tmp_key)
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
                f'SET (key, last_updated) = (\'{key}\', \'{value}\') ' \
                f'WHERE key = \'{key}\';'
        else:
            query = f'INSERT INTO {state_table} VALUES (\'{key}\', TIMESTAMP \'{value}\');'

        self.cursor.execute(query)
        self.connection.commit()

    def _create_staging_table(self, table):
        staging_table = f'{table}_staging'
        self.cursor.execute(f'CREATE TABLE {staging_table} (LIKE {table});')
        self.connection.commit()  # TODO: Check if necessary after redshift (should be same tx).
        return staging_table

    def _load_staging_table(self, staging_table, s3_tmp_key):
        # TODO: rewrite this ugly stuff when redshift cluster is available
        # temporary local import
        import subprocess
        f_name = s3_tmp_key.split("/")[1]
        cmd = f'aws s3 cp s3://sb-extract-test/{s3_tmp_key} . && gunzip ./{f_name} && PGPASSWORD={self.password} ' \
            f'psql -h {self.host} -p {self.port} -U {self.user} ' \
            f'-d {self.db_name} -c "\COPY {staging_table} ' \
            f'FROM \'./{f_name.replace(".gz", "")}\' ' \
            f'WITH DELIMITER \'|\' NULL \'\'"'
        cp_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)

    def _deduplicate_and_insert(self, table, staging_table):
        query = f'''
        WITH deduplicated_keys AS (
            SELECT stg.key
            FROM {staging_table} stg
            EXCEPT 
            SELECT t.key
            FROM {table} t
        )
        INSERT INTO {table}
        SELECT stg.*
        FROM deduplicated_keys dk
        INNER JOIN {staging_table} stg ON stg.key = dk.key;
        '''
        self.cursor.execute(query)

    def _drop_staging_table(self, staging_table):
        self.cursor.execute(f'DROP TABLE {staging_table};')
