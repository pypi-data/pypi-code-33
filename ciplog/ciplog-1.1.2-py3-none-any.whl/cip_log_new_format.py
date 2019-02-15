from datetime import datetime
import os
import glob
import logging
import logging.handlers
import logging.config
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from .json_log_formatter import JSONFormatter


SERVICE_NAME = "cip_log"
LOG_PATH = "{}/log/".format(os.getcwd())
GIT_TAG = "0.0.0"
ENVIRONMENT = 'NAO INFORMADO'


ERROR = {
    'code': "HS001",
    'message': 'valor do status HTTP é inválido'
}


class CipLogNewFormat(object):

    def __init__(self, service_ip, service_name=SERVICE_NAME, log_path=LOG_PATH, scope_name=__name__):

        self._max_file_size = 500000
        self._log_folder = log_path
        self.service_name = service_name
        self.service_version = os.getenv('GIT_TAG', GIT_TAG)
        self.service_ip = service_ip
        self.environment = os.getenv('ENVIRONMENT', ENVIRONMENT)

        self.create_folder()

        file_name = datetime.now().strftime('%d-%m-%Y.log')
        file_path = "{0}{1}".format(self._log_folder, file_name)
        formatter = JSONFormatter()

        file_handler = RotatingFileHandler(
            file_path, maxBytes=self._max_file_size, backupCount=20)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        stream_handler = StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)

        self._logger = logging.getLogger(scope_name)
        self._logger.addHandler(file_handler)
        self._logger.addHandler(stream_handler)
        self._logger.setLevel(logging.DEBUG)

    def create_folder(self):
        if not os.path.exists(self._log_folder):
            os.makedirs(self._log_folder)

    def path(self):
        """Return the path of the logs folder.
        For default, path is your folder.
        """
        return self._log_folder

    def service_name_log(self):
        """service name that used in info, warning and error."""
        return self.service_name

    def service_version_log(self):
        """service version thats used in info, warning and error."""
        return self.service_version

    def count_log_files(self):
        """Return number of log files."""
        return len(glob.glob("{0}/*.log*".format(self._log_folder)))

    def get_log_files(self):
        """Return all logs files."""
        return glob.glob("{0}/*.log*".format(self._log_folder))

    def delete_log_files(self):
        for file in glob.glob("{0}/*.log*".format(self._log_folder)):
            try:
                os.remove(file)
            except IOError as io:
                self.error("erro ao excluir")

    def debug(self, message):
        self._logger.debug(message)

    def info(self, class_name, method, data, browser=None, user_ip=None, service_name=None, message=None):
        """This module write in a log file.

        Args:
            - status (int): Is a HTTP response status code.
            - service_name (str): Service name of the application
            - service_version (str): Service version of the application
            - message (str): one message about the log.
        Returns:
            The return value. True for success, False otherwise.
        """
        if service_name is None:
            service_name = self.service_name

        """
        Montar um json dinâmico com as propriedades opcionais para
        e adicionar esse json com a mensagem
        """
        dinamic_data = self.mount_dinamic_data(browser, user_ip)

        self._logger.info(
            message, extra={'level': 'INFO', 'class_name': class_name,
                            'method': method, 'data': str(data), 'dinamic_data': dinamic_data,
                            'service_name': service_name, 'service_version': self.service_version,
                            'service_ip': self.service_ip, 'environment': self.environment})

    def warning(self, code, class_name, method, data, browser=None, user_ip=None, service_name=None, message=None):
        """This module write in a log file.

        Args:
            - code (str): One value that define the message log.
            - service_name (str): Service name of the application
            - service_version (str): Service version of the application
            - message (str): one message about the log.
        Returns:
            The return value. True for success, False otherwise.
        """
        if service_name is None:
            service_name = self.service_name

        """
        Montar um json dinâmico com as propriedades opcionais para
        e adicionar esse json com a mensagem
        """
        dinamic_data = self.mount_dinamic_data(browser, user_ip)

        self._logger.warning(
            message, extra={'level': 'WARNING', 'code': code, 'class_name': class_name,
                            'method': method, 'data': str(data), 'dinamic_data': dinamic_data,
                            'service_name': service_name, 'service_version': self.service_version,
                            'service_ip': self.service_ip, 'environment': self.environment})

    def error(self, code, class_name, method, data, browser=None, user_ip=None, service_name=None, message=None):
        """This module write in a log file.

        Args:
            - code (str): One value that define the message log.
            - status (int): Is a HTTP reponse status code.
            - service_name (str): Service name of the application
            - service_version (str): Service version of the application
            - message (str): one message about the log.
        Returns:
            The return value. True for success, False otherwise.
        """
        if service_name is None:
            service_name = self.service_name

        """
        Montar um json dinâmico com as propriedades opcionais para
        e adicionar esse json com a mensagem
        """
        dinamic_data = self.mount_dinamic_data(browser, user_ip)

        self._logger.error(
            message, extra={'level': 'ERROR', 'code': code, 'class_name': class_name,
                            'method': method, 'data': str(data), 'dinamic_data': dinamic_data,
                            'service_name': service_name, 'service_version': self.service_version,
                            'service_ip': self.service_ip, 'environment': self.environment},
            exc_info=True)

    @staticmethod
    def mount_dinamic_data(browser, user_ip):
        dinamic_data = {}
        if browser is not None:
            dinamic_data['browser'] = str(browser)

        if user_ip is not None:
            dinamic_data['user_ip'] = str(user_ip)

        return dinamic_data
