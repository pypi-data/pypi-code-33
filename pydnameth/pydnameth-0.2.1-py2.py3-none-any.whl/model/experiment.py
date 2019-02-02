from pydnameth.model.context import Context
from pydnameth.config.setup.types import Experiment


def base(config):
    config.initialize()
    context = Context(config)
    context.base_pipeline(config)


def advanced(config, configs_primary):
    config.initialize()
    for config_primary in configs_primary:
        config_primary.initialize()
    context = Context(config)
    context.advanced_pipeline(config, configs_primary)


def plot(config, configs_primary):
    config.initialize()
    for config_primary in configs_primary:
        config_primary.initialize()
    context = Context(config)
    context.plot_pipeline(config, configs_primary)


def run(config, configs_primary=None):
    if config.setup.experiment == Experiment.base:
        base(config)
    elif config.setup.experiment == Experiment.advanced:
        advanced(config, configs_primary)
    elif config.setup.experiment == Experiment.plot:
        plot(config, configs_primary)
