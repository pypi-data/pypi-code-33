# TODO use modern API

import ruamel.yaml


def read_config_file(config_path):
    """
    Read a config.yaml file and return as a dictionary.
    """
    with open(config_path, "r") as f:
        config_dict = ruamel.yaml.load(f.read(), Loader=ruamel.yaml.Loader)

    return config_dict


def write_config_file(write_path, config_dict):
    """
    Write yaml dictionary to `write_path`.
    """
    with open(write_path, "w") as f:
        f.write(ruamel.yaml.dump(config_dict, default_flow_style=False))
