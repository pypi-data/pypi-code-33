import json
import logging
import logging.handlers
from datetime import datetime
from os import environ
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.settings import Settings, Constants

LOG_FILE_ENV = 'LOGFILE'
LOG_FILE_DEFAULT = f'{Settings.SERVICE_NAME}.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL_ENV = 'LOGLEVEL'
LOG_LEVEL_DEFAULT = 'ERROR'


class PingLogFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    def filter(self, record):
        return 'ping' not in record.getMessage()


def _get_logger(module_name):
    logging.basicConfig(level=environ.get(LOG_LEVEL_ENV, LOG_LEVEL_DEFAULT), format=LOG_FORMAT)
    logger = logging.getLogger(module_name)
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.FileHandler(environ.get(LOG_FILE_ENV, LOG_FILE_DEFAULT))
    handler.setFormatter(formatter)
    handler.addFilter(PingLogFilter())
    global_logging = logging.getLogger()
    for handler_def in global_logging.handlers:
        handler_def.addFilter(PingLogFilter())
    logger.addHandler(handler)
    return logger


# noinspection PyBroadException
class SumoLogClient:
    def __init__(self, http_client=HttpRequestor(), log_url=Settings.REMOTE_LOG_URL):
        self.client = http_client
        self.log_url = log_url

    @staticmethod
    def get_environment(region=Settings.AWS_REGION):
        environment = Constants.UAT
        if region == Constants.PROD_REGION:
            environment = Constants.PROD
        return environment

    def get_headers(self, service):
        account = Settings.AWS_ACCOUNT
        environment = self.get_environment()
        version = Settings.VERSION
        return {
            Constants.SUMO_CATEGORY_HEADER_KEY: Constants.SUMO_CATEGORY,
            Constants.SUMO_HOST_HEADER_KEY: Constants.SUMO_HOST_HEADER.format(
                account=account, environment=environment, version=version, service=service),
            Constants.CONTENT_TYPE_HEADER: Constants.CONTENT_TYPE_JSON}

    @staticmethod
    def get_log_message(level, service, message):
        log_data = {Constants.SUMO_MESSAGE_KEY: message,
                    Constants.SUMO_LEVEL_KEY: level,
                    Constants.SERVICE: service,
                    Constants.SUMO_TIMESTAMP_KEY: datetime.now().strftime(Constants.SUMO_TIMESTAMP_FORMAT)}
        return json.dumps(log_data, default=str)

    def ship_log(self, level, service, message):
        try:
            header = self.get_headers(service)
            log_message = self.get_log_message(level, service, message)
            result = self.client.post(Settings.REMOTE_LOG_URL, data=log_message, headers=header)
            return result.status_code == 200
        except Exception:  # pylint: disable=broad-except
            return False


class Logger:
    logger = _get_logger(Settings.SERVICE_NAME)

    def __init__(self, service_name=Settings.SERVICE_NAME, logger=None, remote_client=SumoLogClient()):
        self.name = service_name
        self.log_name = service_name
        self.remote_log = remote_client
        if logger:
            self.logger = logger

    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)
        self.remote_log.ship_log(Logger.debug.__name__, self.name, message)

    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
        self.remote_log.ship_log(Logger.error.__name__, self.name, message)

    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)
        self.remote_log.ship_log(Logger.info.__name__, self.name, message)

    def critical(self, message, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)
        self.remote_log.ship_log(Logger.critical.__name__, self.name, message)


class LoggingProvider(Logger):
    def worker_setup(self, worker_ctx):
        self.log_name = worker_ctx.service_name

    def get_dependency(self, _):
        return self.logger


def log_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            Logger().error(f'Error during {func.__name__} {ex}', exc_info=True)
            raise
    return wrapper
