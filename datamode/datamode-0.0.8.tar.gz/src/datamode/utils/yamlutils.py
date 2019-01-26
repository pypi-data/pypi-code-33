import os, yaml


def load_yaml(CONFIG_DIR):
  """
  Searches for datamode.yml in:
    (1) User defined DATAMODE_CONFIG_DIR environment variable
    (2) The same directory where code was executed.
    (3) ~/.datamode/

  CONFIG_DIR is defined in settings.py
  """
  yaml_config = None

  if os.environ.get('DATAMODE_CONFIG_DIR', None):
    yaml_filepath = os.path.join(os.environ['DATAMODE_CONFIG_DIR'], 'datamode.yml')
  elif os.path.isfile(os.path.join(os.getcwd(), 'datamode.yml')):
    yaml_filepath = os.path.join(os.getcwd(), 'datamode.yml')
  elif os.path.isfile(os.path.join(CONFIG_DIR, 'datamode.yml')):
    yaml_filepath = os.path.join(CONFIG_DIR, 'datamode.yml')
  else:
    yaml_filepath = None

  if yaml_filepath:
    with open(yaml_filepath, 'r') as ymlf:
      yaml_config = yaml.load(ymlf)

  return yaml_filepath, yaml_config
