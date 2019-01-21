import psycopg2 as pg2


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

    def load_table(self, table, key):
        """
        Temporary implementation for RDS copy from local terminal.
        Should be redshift COPY statement instead

        :param table: table name to load data to
        """

        # temporary local import
        import subprocess
        f_name = key.split("/")[1]
        cmd = f'aws s3 cp s3://sb-extract-test/{key} . && gunzip ./{f_name} && PGPASSWORD={self.password} ' \
            f'psql -h {self.host} -p {self.port} -U {self.user} ' \
            f'-d {self.db_name} -c "\COPY {table} ' \
            f'FROM \'./{f_name.replace(".gz", "")}\' ' \
            f'WITH DELIMITER \'|\' NULL \'\'"'
        cp_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
