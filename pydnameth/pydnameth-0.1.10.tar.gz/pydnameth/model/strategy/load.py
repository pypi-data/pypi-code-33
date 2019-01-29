import abc
from pydnameth.config.setup.types import Task
from pydnameth.infrastucture.load.cpg import load_cpg
from pydnameth.infrastucture.load.table import load_table_dict


class LoadStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load_base(self, config):
        pass

    @abc.abstractmethod
    def load_advanced(self, config, configs_primary):
        pass

    @abc.abstractmethod
    def load_plot(self, config, configs_primary):
        pass

    @abc.abstractmethod
    def inherit_base(self, source_config, target_config):
        pass


class CPGLoadStrategy(LoadStrategy):

    def load_base(self, config):
        load_cpg(config)
        config.base_list = config.cpg_list
        config.base_dict = config.cpg_dict
        config.base_data = config.cpg_data

    def load_advanced(self, config, configs_primary):
        self.load_base(config)
        for config_primary in configs_primary:
            self.inherit_base(config, config_primary)
            if config.setup.task is Task.table:
                config_primary.advanced_data = load_table_dict(config_primary)
                config_primary.advanced_list = config_primary.base_list
                config_primary.advanced_dict = {}
                row_id = 0
                for item in config_primary.advanced_data['item']:
                    config_primary.advanced_dict[item] = row_id
                    row_id += 1

    def load_plot(self, config, configs_primary):
        self.load_base(config)
        for config_primary in configs_primary:
            self.inherit_base(config, config_primary)

        config.plot_data = {
            'data': [],
            'fig': []
        }

    def inherit_base(self, config_source, config_target):
        config_target.base_list = config_source.base_list
        config_target.base_dict = config_source.base_dict
        config_target.base_data = config_source.base_data


class AttributesLoadStrategy(LoadStrategy):

    def load_base(self, config):
        pass

    def load_advanced(self, config, configs_primary):
        pass

    def load_plot(self, config, configs_primary):
        config.plot_data = {
            'data': [],
            'fig': []
        }

    def inherit_base(self, config_source, config_target):
        pass
