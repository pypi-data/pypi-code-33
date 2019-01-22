import os
import yaml
import keras

TEXT_VECTORIAN_CONFIG_FILENAME = 'config.yml'
text_vectorian_config = None
DOWNLOAD_ROOT='.text_vectorian'

def get_package_directory():
    package_directory = os.path.dirname(os.path.abspath(__file__))

    return package_directory

def load_config():
    config_filename = os.path.join(get_package_directory(), TEXT_VECTORIAN_CONFIG_FILENAME)
    global text_vectorian_config

    if not text_vectorian_config:
        with open(config_filename, 'r') as f:
            text_vectorian_config = yaml.load(f)

    return text_vectorian_config

def get_absolute_filename(filename):
    return os.path.join(get_package_directory(), filename)

def load_model(modulename, typename, config):
    name = config[modulename][typename]['models']['name']
    url = config[modulename][typename]['models']['url']
    filename = keras.utils.get_file(name, url, cache_dir=DOWNLOAD_ROOT, cache_subdir='.models')

    print(filename)

    return filename