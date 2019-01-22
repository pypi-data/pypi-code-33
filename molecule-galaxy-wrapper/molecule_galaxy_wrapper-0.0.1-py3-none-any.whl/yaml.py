import yaml

requirements = {}
meta = {}


def load(path):
    """Reads the yaml file and returns the content """
    with open(path, 'r') as stream:
        return yaml.load(stream)


def dump(path, content):
    """ Writes the yaml content into the file """
    with open(path, mode='w') as stream:
        yaml.dump(content, stream)
