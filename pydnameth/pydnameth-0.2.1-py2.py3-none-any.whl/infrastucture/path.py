import os.path
from pydnameth.config.data.types import DataType


def get_data_base_path(config):
    return config.data.get_data_base_path()


def get_cache_path(config):
    path = get_data_base_path(config) + '/' + \
           DataType.cache.value + '/' + \
           str(config.annotations)

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def get_save_path(config):
    path = str(config.data) + '/' + \
           str(config.setup) + '/' + \
           str(config.annotations) + '/' + \
           str(config.attributes)

    if not os.path.exists(path):
        os.makedirs(path)

    return path
