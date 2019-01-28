from google.cloud import bigquery

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class bigquery_io(object):

    _certificate_filename = 'certificates/aether-bigquery-adminsdk-0dc610901023.json'
    _default_resource_metadata_dataset_name = 'ae_data_platform_resource_metadata_dataset'
    _project_id = 'aether-185123'

    def create_table(self, table):
        self._client.create_table(table)

    def table_exists(self, table):
        try:
            self._client.get_table(table)
            return True
        except :
            return False

    def load_table_from_file(self, csv_file, table_ref, job_config):
        return self._client.load_table_from_file(csv_file, table_ref, job_config=job_config)

    def __init__(self):
        self._client = bigquery.Client.from_service_account_json(self._certificate_filename)
