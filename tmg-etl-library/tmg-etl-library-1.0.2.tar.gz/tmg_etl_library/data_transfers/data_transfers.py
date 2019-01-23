from tmg_etl_library.data_transfers.transfer import Transfer
from tmg_etl_library.components.config import *

from tmg_etl_library.components.databases import bq, mysql
from tmg_etl_library.components.locals import csv

import uuid


class BQTOBQ(Transfer):
    def __init__(self, log, source, target, config=BQTOBQConfig()):
        super().__init__(log, source, target, config)
        self.id = uuid.uuid4()
        self.source = source
        self.target = target
        if not isinstance(config, BQTOBQConfig):
            raise TypeError('Config Must be of Type: BQTOBQConfig')
        self.config = config
        self.log = log
        self.bq_client = bq.BQClient(self.log, source.project if source else target.project)

    def run(self):
        if self.config.query:
            self.bq_client.run_query(query=self.config.query, query_file_name=self.config.query_file_name,
                                     destination=self.target,
                                     write_disposition=self.config.write_disposition,
                                     use_legacy_sql=self.config.use_legacy_sql,
                                     async_query=self.config.async_query)
        else:
            self.bq_client.copy_tables(source=self.source, target=self.target, config=self.config)


class BQTOCSV(Transfer):
    def __init__(self, log, BQTable, CSVFile, config=BQTOCSVConfig()):
        super().__init__(log, BQTable, CSVFile, config)
        self.id = uuid.uuid4()
        self.BQTable = BQTable
        self.CSVFile = CSVFile
        if not isinstance(config, BQTOCSVConfig):
            raise TypeError('Config Must be of Type: BQTOCSVConfig')
        self.config = config
        self.log = log
        self.bq_client = bq.BQClient(self.log, BQTable.project)

    def run(self):
        if self.config.full_table:
            self.bq_client.full_table_to_file(self.BQTable, self.CSVFile, self.config)
        elif self.config.query:
            self.bq_client.query_to_file(self.config.query, self.CSVFile, self.config)
        else:
            raise TypeError("Either 'full_table' or 'query' must be set in the BQTOCSVConfig class")


class BQTOMySQL(Transfer):
    def __init__(self, log, source, target, config=BQTOMySQLConfig()):
        super().__init__(log, source, target, config)
        self.id = uuid.uuid4()
        self.source = source
        self.target = target
        if not isinstance(config, BQTOMySQLConfig):
            raise TypeError('Config Must be of Type: BQTOMySQLConfig')
        self.config = config
        self.log = log

    def run(self):
        pass


class CSVTOBQ(Transfer):
    def __init__(self, log, CSVFile, BQTable, config=CSVTOBQConfig()):
        super().__init__(log, CSVFile, BQTable, config)
        self.id = uuid.uuid4()
        self.CSVFile = CSVFile
        self.BQTable = BQTable
        if not isinstance(config, CSVTOBQConfig):
            raise TypeError('Config Must be of Type: CSVTOBQConfig')
        self.config = config
        self.log = log
        self.bq_client = bq.BQClient(self.log, BQTable.project)

    def run(self):
        self.bq_client.insert_csv(self.CSVFile, self.BQTable, self.config)


class CSVTOMySQL(Transfer):
    def __init__(self, log, source, target, config=CSVTOMySQLConfig()):
        super().__init__(log, source, target, config)
        self.id = uuid.uuid4()
        self.source = source
        self.target = target
        if not isinstance(config, CSVTOMySQLConfig):
            raise TypeError('Config Must be of Type: CSVTOMySQLConfig')
        self.config = config
        self.log = log

    def run(self):
        pass


class MySQLTOBQ(Transfer):
    def __init__(self, log, source, target, config=MySQLTOBQConfig()):
        super().__init__(log, source, target, config)
        self.id = uuid.uuid4()
        self.source = source
        self.target = target
        if not isinstance(config, MySQLTOBQConfig):
            raise TypeError('Config Must be of Type: MySQLTOBQConfig')
        self.config = config
        self.log = log

    def run(self):
        pass

