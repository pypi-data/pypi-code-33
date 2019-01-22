import components.locals as l
import components.databases as db
import time
import uuid


class XTransfer:

    def __init__(self, log, source_client, source, target_client, target, mappings=None, configuration=None):
        """
        :param log: Logger object
        :param source_client Client to be used to interact with the data source (BQClient, BTClient, FTPClient, ...)
        :param source: Data source (BQTable, BTTable, MySQLTable, CSVFile....) object
        :param target_client: Client to be used to interact with the target source (BQClient, BTClient, FTPClient, ...)
        :param target: Data target (BQTable, BTTable, MySQLTable, CSVFile....) object
        :param mappings: Defines or to map data from source to target
        :param configuration: Dictionary that contains any extra configuration for x-transfer
        """
        self.logger = log
        self.source_client = source_client
        self.source = source
        self.target_client = target_client
        self.target = target
        self.mappings = mappings
        self.configuration = configuration
        self.id = uuid.uuid4()
        # Generate clients inside the transfer.
        self.logger.info("Data transfer with id {} created".format(self.id))

    def run(self):
        """
        Runs the data transfer moving data from source to target based on source type, target type and defined mappings
        :return: Boolean to define if a data transfer has been successfully or not.
        """

        self.logger.info("Running data transfer {}".format(self.id))
        if type(self.source) is l.csv.CSVFile and type(self.target) is db.bq.BQTable:
            self.from_csv_to_bq()
        else:
            pass
        self.logger.info("Data transfer {} executed successfully".format(self.id))

    def from_csv_to_bq(self):
        """
        Transfers data from CSV to BQ based on the current x-transfer configuration
        :return:
        """

        # The process doesn't create a table if doesn't exists it might be passed as an option in configuration
        # Mapping is not used in this specific case since it assumes that the table already exists.
        table_ref = self.target_client.get_table_ref(self.target)
        if not table_ref:
            raise Exception("Table does not exists")

        with open(self.source.path, mode="rb") as csv_file:
            if self.configuration:
                job = self.target_client.run_job(table_ref, csv_file, 'CSV', self.source.delimiter, **self.configuration)
            else:
                job = self.target_client.run_job(table_ref, csv_file, 'CSV', self.source.delimiter)

            while True:
                job.reload()  # Refreshes the state via a GET request.
                if job.state == 'DONE':
                    if job.error_result:
                        raise RuntimeError(job.errors)
                    break
                time.sleep (1)
            # job.result()  # Waits for table load to complete.


class PushPullTransfer:
    #TODO: think about what would happen if target is a CSV
    #TODO: how would you transfer from BQ to BQ (dont want to use functions outside of Transfer class)

    def __init__(self, log, source, target, mappings=None, source_config=None, target_config=None):
        """
        :param log: Logger object
        :param source_client Client to be used to interact with the data source (BQClient, BTClient, FTPClient, ...)
        :param source: Data source (BQTable, BTTable, MySQLTable, CSVFile....) object
        :param target_client: Client to be used to interact with the target source (BQClient, BTClient, FTPClient, ...)
        :param target: Data target (BQTable, BTTable, MySQLTable, CSVFile....) object
        :param mappings: Defines or to map data from source to target
        :param configuration: Dictionary that contains any extra configuration for x-transfer
        """
        self.logger = log
        self.source = source
        self.target = target
        self.mappings = mappings
        self.id = uuid.uuid4()
        self.source_config = source_config
        self.target_config = target_config
        # Generate clients inside the transfer.
        self.logger.info("Data transfer with id {} created".format(self.id))

    def run(self):
        """
        Runs the data transfer moving data from source to target based on source type, target type and defined mappings
        :return: Boolean to define if a data transfer has been successfully or not.
        """

        self.logger.info("Running data transfer {}".format(self.id))
        tmp_file = '/tmp/%s.csv' % self.id
        self.source.pull(config=self.source_config, tmp_file=tmp_file, logger=self.logger)
        self.target.push(config=self.target_config, tmp_file=tmp_file, logger=self.logger)
        self.logger.info("Data transfer {} executed successfully".format(self.id))


