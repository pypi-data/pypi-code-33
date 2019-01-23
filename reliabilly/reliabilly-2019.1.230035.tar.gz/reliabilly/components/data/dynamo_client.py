from uuid import uuid4
from decimal import Decimal
import boto3
import botocore
from reliabilly.components.data import DataClient, get_query
from reliabilly.components.logger import Logger, log_exception
from reliabilly.components.monitoring import monitor, MonitoringProvider
from reliabilly.settings import Constants, Settings


def get_default_dynamo_resource(client=boto3.resource):  # pragma: no cover
    endpoint_url = None
    # Prevent unit tests from stalling in Windows environments
    if not Settings.USE_DYNAMO:
        return None
    config = botocore.client.Config(
        connect_timeout=Constants.DEFAULT_AWS_CONNECT_TIMEOUT,
        retries={Constants.AWS_MAX_RETRY_ATTEMPTS: Constants.DEFAULT_AWS_MAX_RETRY_COUNT})
    if not Settings.ENV:
        endpoint_url = f'{Settings.DYNAMO_URL}:{Settings.DYNAMO_PORT}'
    return client(Constants.DYNAMO_RESOURCE_KEY, region_name=Settings.AWS_REGION,
                  endpoint_url=endpoint_url, config=config)


def get_default_dynamo_client():
    return get_default_dynamo_resource(boto3.client)


# noinspection PyBroadException
class DynamoDataClient(DataClient):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = Logger()
        self.table_name = kwargs.get(Constants.TABLE, Settings.SERVICE_NAME)
        self.client = kwargs.get(Constants.CLIENT, get_default_dynamo_client())
        self.resource = kwargs.get(Constants.RESOURCE, get_default_dynamo_resource())
        self._initialize_tables()

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_create'))
    def create(self, model):
        model = self.get_converted_model(model)
        result = self.resource.Table(self.table_name).put_item(Item=model)
        return self.check_status(result)

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_update'))
    def update(self, key, model):
        model.id = key
        return self.create(model)

    def get_converted_model(self, model, nest=False):
        empty_keys = list()
        if not isinstance(model, dict):
            model = model.__dict__
        for key, value in model.items():
            if isinstance(value, float):
                model[key] = Decimal(str(value))
                continue
            if not value:
                if key not in empty_keys:
                    empty_keys.append(key)
                continue
            if isinstance(value, dict):
                model[key] = self.get_converted_model(value, True)
                if not model[key]:
                    if key not in empty_keys:
                        empty_keys.append(key)
        for key in empty_keys:
            model.pop(key)
        if not nest:
            if Constants.ID not in model.keys():
                model[Constants.ID] = str(uuid4())
        return model

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_get'))
    def get(self, key):
        self.logger.debug(f'Get item on dynamo for id: {key}')
        self.create_table(self.table_name)
        return self.resource.Table(self.table_name).get_item(Key={Constants.ID: key}).get(
            Constants.DYNAMO_ITEM_KEY, None)

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_get_specific'))
    def get_specific(self, id_value, table_name):
        self.logger.debug(f'Get specific item on dynamo for id: {id_value} from {table_name}')
        self.create_table(self.table_name)
        return self.resource.Table(self.table_name).get_item(
            Key={Constants.ID: id_value}).get(Constants.DYNAMO_ITEM_KEY, None)

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_find'))
    def find(self, key, value):
        self.logger.debug(f'Find called on dynamo key: {key} val: {value}')
        all_items = self.get_all()
        return self.find_item_in_list(all_items, **{key: value})

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_get_all'))
    def get_all(self):
        self.logger.debug(f'Get all called on dynamo')
        self.create_table(self.table_name)
        return self.resource.Table(self.table_name).scan().get(Constants.DYNAMO_ITEMS_KEY, [])

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_count'))
    def count(self):
        return self.resource.Table(self.table_name).scan().get(Constants.DYNAMO_COUNT_KEY, 0)

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_purge'))
    def purge(self):
        self.logger.debug('Purge called on dynamo...')
        success = True
        items = self.get_all()
        for item in items:
            success = success and self.delete(item.get(Constants.ID))
        return success

    @log_exception
    @monitor(monitor_name=MonitoringProvider.get_monitor_prefix(Settings.SERVICE_NAME, 'dynamo_delete'))
    def delete(self, key):
        self.logger.debug(f'Delete on dynamo called id: {key}')
        result = self.resource.Table(self.table_name).delete_item(Key={Constants.ID: key})
        return self.check_status(result)

    @staticmethod
    def check_status(result):
        return result.get(Constants.DYNAMO_RESPONSE_METADATA, {}).get(
            Constants.DYNAMO_SUCCESS_STATUS, Constants.BAD_REQUEST_CODE) == Constants.SUCCESS_RESPONSE_CODE

    @log_exception
    def table_exists(self, table_name):
        try:
            return self.resource.Table(table_name).table_status == 'ACTIVE'
        except Exception:  # pylint: disable=broad-except
            return False

    @log_exception
    def delete_table(self, table_name):
        try:
            return self.check_status(self.client.delete_table(TableName=table_name))
        except Exception:  # pylint: disable=broad-except
            return False

    @log_exception
    def filter(self, **kwargs):
        if not kwargs:
            items = self.get_all()
            return items, 0, len(items), len(items)
        offset, limit, query = get_query(**kwargs)
        all_items = self.get_all()
        return self.find_items_in_list(all_items, offset, limit, **query)

    @log_exception
    def delete_db(self):
        self.logger.debug('Drop db on dynamo called.')
        return self.delete_table(self.table_name)

    def create_table(self, table_name):
        try:
            if not self.table_exists(table_name):
                self.resource.create_table(AttributeDefinitions=[Constants.DYNAMO_ID_TABLE_ATTR],
                                           KeySchema=[Constants.DYNAMO_ID_TABLE_KEY],
                                           ProvisionedThroughput=Constants.DEFAULT_DYNAMO_THROUGHPUT,
                                           TableName=table_name)
            return True
        except Exception as ex:  # pylint: disable=broad-except
            self.logger.info(f'Error creating dynamo table. {ex}', exc_info=True)
            return False

    @staticmethod
    def _get_dictionary_set(items_dictionary):
        converted_list = list()
        for key, value in items_dictionary.items():
            converted_list.append(f'{key}|{value}')
        return set(converted_list)

    def find_item_in_list(self, all_items, **kwargs):
        args_set = self._get_dictionary_set(kwargs)
        match_list = list()
        for item in all_items:
            item_set = self._get_dictionary_set(item)
            if len(item_set.intersection(args_set)) == len(args_set):
                match_list.append(item)
        return match_list

    def find_items_in_list(self, all_items, offset, limit, **kwargs):
        self.logger.info(f'Find called on dynamo with {offset}, {limit}')
        match_list = self.find_item_in_list(all_items, **kwargs)
        return match_list, offset, limit, len(match_list)

    def _tag_table(self, table_arn):
        try:
            self.client.tag_resource(ResourceArn=table_arn, Tags=Constants.DYNAMO_TAGS)
        except Exception:  # pylint: disable=broad-except
            pass

    def _initialize_tables(self):
        if self.create_table(self.table_name):
            self._tag_table(self.resource.Table(self.table_name).table_arn)

    def get_status(self):
        return self.table_exists(self.table_name)
