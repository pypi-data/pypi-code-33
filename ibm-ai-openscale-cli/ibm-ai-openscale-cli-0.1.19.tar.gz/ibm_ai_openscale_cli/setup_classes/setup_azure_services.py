# coding=utf-8
from ibm_ai_openscale_cli.setup_classes.setup_services import SetupServices
import logging

logger = logging.getLogger(__name__)

class SetupAzureServices(SetupServices):

    def __init__(self, args, environment):
        super().__init__(args, environment)

    def setup_azureml(self):
        logger.info('Azure instance specified')
        return self._read_credentials_from_file(self.args.azure)