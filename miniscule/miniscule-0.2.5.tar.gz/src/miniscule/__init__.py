import os
import yaml


class ConfigLoader(yaml.SafeLoader):
    # pylint: disable=too-many-ancestors
    def __init__(self, stream):
        super(ConfigLoader, self).__init__(stream)
        yaml.add_constructor('!or', or_constructor, Loader=ConfigLoader)
        yaml.add_constructor('!env', env_constructor, Loader=ConfigLoader)


def or_constructor(loader, node):
    for expr in loader.construct_sequence(node):
        if expr is not None:
            return expr
    return None


def env_constructor(loader, node):
    name = loader.construct_yaml_str(node)
    if name in os.environ:
        return yaml.load(os.getenv(name))
    return None


def load_config(stream, Loader=ConfigLoader):
    return yaml.load(stream, Loader)


def read_config(path, Loader=ConfigLoader):
    with open(path, 'r') as stream:
        return load_config(stream, Loader=Loader)
