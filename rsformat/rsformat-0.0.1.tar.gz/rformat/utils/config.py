import yaml
import os


def default_config():
    """
    Returns the default options rformat will use
    """
    return {
       "log_level": "DEBUG"
    }

def parse_yaml(confpath):
    """
    Loads yaml from a config file path does not support arbitrary code in yaml
    """
    try:
        filepath = os.path.abspath(confpath)
    except:
        raise TypeError("config not string type required to specify path: %s" % confpath)
    with open(filepath, 'r') as f:
        configs = yaml.safe_load(f)

    return configs
        
     
        