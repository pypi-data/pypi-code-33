import yaml as yaml_
from clav.data import ottr
from clav.data.format import myaml
from clav.data.format.base import Format
from clav.os import dump

def yaml_set_dict_type(dict_type):
  'Configure yaml to use a user-supplied type for backing dicts.'

  def representer(dumper, data):
    return dumper.represent_dict(data.items())
  def constructor(loader, node):
    return dict_type(loader.construct_pairs(node))
  tag = yaml_.resolver.BaseResolver.DEFAULT_MAPPING_TAG
  yaml_.add_representer(dict_type, representer)
  yaml_.add_constructor(tag, constructor)

class Yaml(Format):
  '''
  Thin wrapper for yaml. This class configures the yaml module to use
  ordered dictionaries for backing dicts, prints yaml which is more
  human-readable, and auto-quotes fields containing ``{{`` and ``}}``
  for compatibility with Ansible.
  '''

  # This class uses a modified version of the myaml module to implement
  # the dump*() methods.

  def __init__(self, dict_type=ottr):
    super().__init__()
    yaml_set_dict_type(dict_type)

  def loads(self, data):
    'Load yaml from string ``data``.'

    return yaml_.load(data)

  def loadf(self, src):
    'Load yaml from file ``src``.'

    with open(src, encoding='utf-8') as fd:
      return self.loads(fd.read())

  def dumps(self, data):
    'Return dict ``data`` as yaml.'

    return myaml.dump(data)

  def dumpf(self, data, dst, encoding='utf-8'):
    'Write dict ``data`` as yaml to file ``dst`` using ``encoding``.'

    return dump(dst, myaml.dump(data), encoding=encoding)

  def dumpfd(self, data, fd):
    'Write dict ``data`` as yaml to file descriptor ``fd``.'

    fd.write(self.dumps(data))
    if hasattr(fd, 'flush') and callable(fd.flush):
      fd.flush()
