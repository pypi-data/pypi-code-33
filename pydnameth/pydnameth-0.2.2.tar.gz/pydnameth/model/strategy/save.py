import abc
from pydnameth.infrastucture.save.figure import save_figure
from pydnameth.infrastucture.save.table import save_table_dict
from pydnameth.infrastucture.path import get_save_path
from pydnameth.infrastucture.file_name import get_file_name
import glob


class SaveStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def save(self, config, configs_child):
        pass

    @abc.abstractmethod
    def is_result_exist(self, config, configs_child):
        pass


class TableSaveStrategy(SaveStrategy):

    def save(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config)
        save_table_dict(fn, config.metrics)

    def is_result_exist(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config) + '.*'
        if glob.glob(fn):
            return True
        else:
            return False


class ClockSaveStrategy(SaveStrategy):

    def save(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config)
        save_table_dict(fn, config.metrics)

    def is_result_exist(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config) + '.*'
        if glob.glob(fn):
            return True
        else:
            return False


class MethylationSaveStrategy(SaveStrategy):

    def save(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config)
        save_figure(fn, config.experiment_data['fig'])

    def is_result_exist(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config) + '.*'
        if glob.glob(fn):
            return True
        else:
            return False


class ObservablesSaveStrategy(SaveStrategy):

    def save(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config)
        save_figure(fn, config.experiment_data['fig'])

    def is_result_exist(self, config, configs_child):
        fn = get_save_path(config) + '/' + \
             get_file_name(config) + '.*'
        if glob.glob(fn):
            return True
        else:
            return False
