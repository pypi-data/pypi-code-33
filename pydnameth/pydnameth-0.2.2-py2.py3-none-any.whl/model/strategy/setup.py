import abc
from pydnameth.config.experiment.types import get_default_params
from pydnameth.config.experiment.types import get_metrics_keys
import math


class SetupStrategy(metaclass=abc.ABCMeta):

    def __init__(self, get_strategy):
        self.get_strategy = get_strategy

    @abc.abstractmethod
    def setup(self, config, configs_child):
        pass

    def setup_params(self, config):
        default_params = get_default_params(config.experiment)
        if not bool(config.experiment.params):
            config.experiment.params = default_params
        else:
            for dp in default_params:
                if dp not in config.experiment.params:
                    config.experiment.params[dp] = default_params[dp]

    def setup_metrics(self, config):
        config.metrics = {}
        for key in get_metrics_keys(config.experiment):
            config.metrics[key] = []


class TableSetUpStrategy(SetupStrategy):

    def setup(self, config, configs_child):
        self.setup_params(config)
        self.setup_metrics(config)

        for config_child in configs_child:
            metrics_keys = get_metrics_keys(config.experiment)
            metrics_keys_child = get_metrics_keys(config_child.experiment)
            for key in metrics_keys_child:
                if key not in metrics_keys:
                    key_primary = key + '_' + str(config_child.attributes.observables)
                    config.metrics[key_primary] = []


class ClockSetUpStrategy(SetupStrategy):

    def setup(self, config, configs_child):
        self.setup_params(config)
        self.setup_metrics(config)

        max_size = len(config.attributes_dict[config.attributes.target])
        test_size = math.floor(max_size * config.experiment.params['part'])
        train_size = max_size - test_size

        # In clock task only first base config matters
        table = configs_child[0].advanced_data
        items = table['item'][0:max_size]
        values = self.get_strategy.get_single_base(config, items)

        config.experiment_data = {
            'items': items,
            'values': values,
            'test_size': test_size,
            'train_size': train_size
        }


class MethylationSetUpStrategy(SetupStrategy):

    def setup(self, config, configs_child):
        self.setup_params(config)
        self.setup_metrics(config)

        config.experiment_data = {
            'data': [],
            'fig': []
        }


class ObservablesSetUpStrategy(SetupStrategy):

    def setup(self, config, configs_child):
        self.setup_params(config)
        self.setup_metrics(config)

        config.experiment_data = {
            'data': [],
            'fig': []
        }
