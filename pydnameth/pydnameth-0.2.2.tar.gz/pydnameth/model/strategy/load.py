import abc
from pydnameth.config.experiment.types import Task
from pydnameth.infrastucture.load.cpg import load_cpg
from pydnameth.infrastucture.load.table import load_table_dict


class LoadStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load(self, config, configs_child):
        pass


class CPGLoadStrategy(LoadStrategy):

    def load(self, config, configs_child):
        load_cpg(config)
        config.base_list = config.cpg_list
        config.base_dict = config.cpg_dict
        config.base_data = config.cpg_data

        for config_child in configs_child:
            config_child.base_list = config.base_list
            config_child.base_dict = config.base_dict
            config_child.base_data = config.base_data

        if config.experiment.task == Task.table or config.experiment.task == Task.clock:

            for config_child in configs_child:

                if config_child.experiment.task == Task.table:

                    config_child.advanced_data = load_table_dict(config_child)
                    config_child.advanced_list = config_child.base_list
                    config_child.advanced_dict = {}
                    row_id = 0
                    for item in config_child.advanced_data['item']:
                        config_child.advanced_dict[item] = row_id
                        row_id += 1


class AttributesLoadStrategy(LoadStrategy):

    def load(self, config, configs_child):
        pass
