from functools import partial

from ..results import Result, MonitorResult, IteratorResult
from ..driver import LinkedinDriver
from ..errors import ManagerNotFound

COMMAND_SEPARATOR = '|'


class BaseManager:
    def __init__(self, driver: LinkedinDriver, logger, manager=''):
        self._driver = driver
        self._manager = manager
        self._logger = logger
        self._submanagers = {}

    def _build_command(self, command):
        if self._manager:
            return COMMAND_SEPARATOR.join([self._manager, command])
        return command

    def _execute_command(self, command, *args, **kwargs):
        return self._driver.execute_command(self._build_command(command), *args, **kwargs)

    def add_submanager(self, name, submanager):
        self._logger.info('Adding submanager {}'.format(name))
        self._submanagers[name] = submanager

    def get_submanager(self, name):
        try:
            return self._submanagers[name]
        except KeyError:
            raise ManagerNotFound('Manager {} not found'.format(name))

    def __getattr__(self, item):
        return self.get_submanager(item)

    def __getitem__(self, item):
        return self.get_submanager(item)


class BaseModelManager(BaseManager):

    @classmethod
    def map_model(cls, data):
        return data

    @classmethod
    def get_model_result_class(cls):
        return partial(Result, fn_map=cls.map_model)

    @classmethod
    def get_monitor_result_class(cls):
        return partial(MonitorResult, fn_map=cls.map_model)

    def monitor_model(self):
        return self._execute_command('monitorModel',
                                     result_class=self.get_monitor_result_class())


class BaseCollectionManager(BaseManager):
    MODEL_MANAGER_CLASS = BaseModelManager

    def get_items(self):
        return self._execute_command('getItems', result_class=self.get_iterator_result_class())

    @classmethod
    def get_monitor_result_class(cls):
        return partial(MonitorResult, fn_map=lambda evt: cls.MODEL_MANAGER_CLASS.map_model(evt['item']))

    @classmethod
    def get_iterator_result_class(cls):
        return partial(IteratorResult, fn_map=cls.MODEL_MANAGER_CLASS.map_model)

    @classmethod
    def get_item_result_class(cls):
        return cls.MODEL_MANAGER_CLASS.get_model_result_class()

    def monitor_add(self):
        return self._execute_command('monitorAdd',
                                     result_class=self.get_item_result_class())

    def monitor_remove(self):
        return self._execute_command('monitorRemove',
                                     result_class=self.get_monitor_result_class())
