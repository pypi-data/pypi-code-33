import codecs
from ruamel.yaml import YAML


requirements = {}
meta = {}
yaml = YAML()


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

    # Force --- as the first line of the file
    data = ""
    with codecs.open(path, 'r') as original:
        data = original.read()
    with codecs.open(path, 'w') as modified:
        modified.write("---\n" + data)
