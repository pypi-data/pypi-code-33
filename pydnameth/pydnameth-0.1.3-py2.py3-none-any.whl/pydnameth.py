# -*- coding: utf-8 -*-

"""Main module."""

from pydnameth.config.config import Config
from pydnameth.config.data.data import Data
from pydnameth.config.setup.setup import Setup
from pydnameth.config.setup.types import Experiment, Task, Method
from pydnameth.model.context import Context


def get_config(data,
               setup,
               annotations,
               attributes,
               target):
    config = Config(data, setup, annotations, attributes, target)
    return config


def get_data(name,
             type,
             path,
             base):
    data = Data(name, type, path, base)
    return data


def get_setup(experiment,
              task,
              method,
              params):
    if not isinstance(experiment, Experiment):
        raise ValueError('experiment must be Experiment instance')
    if not isinstance(task, Task):
        raise ValueError('task must be Task instance')
    if not isinstance(method, Method):
        raise ValueError('method must be Method instance')

    setup = Setup(experiment, task, method, params)
    return setup


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
