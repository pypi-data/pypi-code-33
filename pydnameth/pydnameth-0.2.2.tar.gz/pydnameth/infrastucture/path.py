import os.path
from pydnameth.config.experiment.types import DataType


def get_data_base_path(config):
    path = config.data.path + '/' + config.data.base
    return path


def get_cache_path(config):
    path = get_data_base_path(config) + '/' + \
           DataType.cache.value + '/' + \
           str(config.annotations)

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def get_experiment_path(config):
    path = config.data.path + '/' + \
           config.data.base + '/' + \
           config.experiment.type.value + '/' + \
           config.experiment.task.value + '/' + \
           config.experiment.method.value

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def get_save_path(config):
    path = get_experiment_path(config)+ '/' + \
           str(config.hash)

    if not os.path.exists(path):
        os.makedirs(path)

    return path
