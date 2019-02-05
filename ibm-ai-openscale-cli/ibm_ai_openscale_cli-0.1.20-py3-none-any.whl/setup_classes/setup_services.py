# coding=utf-8
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
import logging

logger = logging.getLogger(__name__)

class SetupServices(object):

    def __init__(self, args, environment):
        self.environment = environment
        self.args = args

    def _read_credentials_from_file(self, credentials_file):
        logger.info('\tUsing credentials from "{}"'.format(credentials_file))
        return jsonFileToDict(credentials_file)

    def setup_postgres_database(self):
        if self.args.postgres is not None:
            logger.info('Compose for PostgreSQL instance specified')
            credentials = self._read_credentials_from_file(self.args.postgres)
            return credentials
        return None

    def setup_icd_database(self):
        if self.args.icd is not None:
            logger.info('ICD instance specified')
            credentials = self._read_credentials_from_file(self.args.icd)
            credentials['db_type'] = 'postgresql'
            connection_data = credentials['connection']['postgres']
            hostname = connection_data['hosts'][0]['hostname']
            port = connection_data['hosts'][0]['port']
            dbname = connection_data['database']
            user = connection_data['authentication']['username']
            password = connection_data['authentication']['password']
            credentials['uri'] = 'postgres://{}:{}@{}:{}/{}'.format(user, password, hostname, port, dbname)
            return credentials
        return None

    def setup_db2_database(self):
        if self.args.db2 is not None:
            logger.info('DB2 instance specified')
            credentials = self._read_credentials_from_file(self.args.db2)
            credentials['db_type'] = 'db2'
            return credentials
        return None