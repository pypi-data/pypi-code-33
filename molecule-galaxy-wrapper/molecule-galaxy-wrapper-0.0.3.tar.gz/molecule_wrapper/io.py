import codecs
# import yaml
# from yaml import Loader, SafeLoader
from ruamel.yaml import YAML


requirements = {}
meta = {}
yaml = YAML()

# def construct_yaml_str(self, node):
#     # Override the default string handling function
#     # to always return unicode objects
#     return self.construct_scalar(node)


# Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
# SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


def read_yaml(path):
    """Reads the yaml file and returns the content """
    content = {}
    with codecs.open(path, 'r', encoding='utf8') as stream:
        content = yaml.load(stream)
    return content


def write_yaml(path, content):
    """ Writes the yaml content into the file """
    with codecs.open(path, mode='w', encoding='utf8') as stream:
        yaml.dump(content, stream)
