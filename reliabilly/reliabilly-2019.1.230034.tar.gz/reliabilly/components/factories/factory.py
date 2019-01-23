# pylint: disable=too-few-public-methods
from enum import Enum

from reliabilly.components.authorization import Authorization
from reliabilly.components.collection.collection_manager import CollectionManager
from reliabilly.components.controllers.collection_controller import CollectionController
from reliabilly.components.controllers.data_controller import DataController
from reliabilly.components.data.dynamo_client import DynamoDataClient
from reliabilly.components.data.mongo_client import MongoDataClient
from reliabilly.components.logger import Logger
from reliabilly.components.monitoring import MonitoringProvider
from reliabilly.components.services.newrelic import NewRelicQueryExecutor
from reliabilly.components.services.queuing import MessageQueue
from reliabilly.components.services.sumologic import SumologicQueryExecutor
from reliabilly.components.tools.secret_manager import SecretManager
from reliabilly.components.web.http_requestor import HttpRequestor


class Components:
    class DataClients(Enum):
        MONGODB = 1
        DYNAMODB = 2

    class LogClients(Enum):
        MAIN = 1

    class MonitorClients(Enum):
        STATSD = 1

    class SecretsClients(Enum):
        SECRETS = 1

    class ServiceClients(Enum):
        AUTH = 1
        NEWRELIC = 2
        OKTA = 3
        SUMOLOGIC = 4
        SQS = 5
        HTTP = 6
        COLLECT_MANAGER = 7

    class Controllers(Enum):
        DATA = 1
        COLLECT = 2


class Factory:  # pylint: disable=too-many-return-statements
    @staticmethod
    def create(component_type, **kwargs):
        if isinstance(component_type, Components.DataClients):
            return Factory._create_data_client(component_type, **kwargs)
        if isinstance(component_type, Components.ServiceClients):
            return Factory._create_service_client(component_type, **kwargs)
        if isinstance(component_type, Components.MonitorClients):
            return MonitoringProvider()
        if isinstance(component_type, Components.LogClients):
            return Logger()
        if isinstance(component_type, Components.SecretsClients):
            return SecretManager()
        if isinstance(component_type, Components.Controllers):
            return Factory._create_controller(component_type, **kwargs)
        return None

    @staticmethod
    def _create_controller(component_type, **kwargs):
        if component_type == Components.Controllers.DATA:
            return DataController(**kwargs)
        if component_type == Components.Controllers.COLLECT:
            return CollectionController(**kwargs)
        return None

    @staticmethod
    def _create_data_client(component_type, **kwargs):
        if component_type == Components.DataClients.MONGODB:
            return MongoDataClient(**kwargs)
        if component_type == Components.DataClients.DYNAMODB:
            return DynamoDataClient(**kwargs)
        return None

    @staticmethod
    def _create_service_client(component_type, **kwargs):
        if component_type == Components.ServiceClients.SQS:
            return MessageQueue(**kwargs)
        if component_type == Components.ServiceClients.NEWRELIC:
            return NewRelicQueryExecutor(**kwargs)
        if component_type == Components.ServiceClients.SUMOLOGIC:
            return SumologicQueryExecutor(**kwargs)
        if component_type == Components.ServiceClients.HTTP:
            return HttpRequestor(**kwargs)
        if component_type == Components.ServiceClients.AUTH:
            return Authorization()
        if component_type == Components.ServiceClients.COLLECT_MANAGER:
            return CollectionManager(**kwargs)
        return None
