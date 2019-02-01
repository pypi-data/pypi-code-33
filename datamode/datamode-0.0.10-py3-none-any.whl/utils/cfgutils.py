import os, configparser, datetime

from uuid import uuid4
from pathlib import Path


def init_config():
  """
  Creates a new ConfigParser object with
  usage/auid/expiry hardcoded.

  Set 2 year expiry of auid.  TODO: Refresh module
  """

  initcfg = configparser.ConfigParser()
  initcfg.add_section('usage')
  # uuid4() is more likely to have collisions over uuid1()
  # but uuid1() is not totally anonymous: https://docs.python.org/3/library/uuid.html#uuid.uuid1
  initcfg.set('usage', 'auid', str(uuid4()))
  initcfg.set('usage', 'expiry', str(datetime.datetime.utcnow() + datetime.timedelta(days=730)))

  return initcfg


def save_config(cfg, fpath):
  try:
    with open(fpath, 'w') as f:
      cfg.write(f)
    return True
  except:
    cfg.set('usage', 'auid', 'DEFAULT_AUID_ERROR_SAVING')
    return False


def load_config(CONFIG_DIR):
  """
  Tries to load in 'datamode.info' from the CONFIG_DIR
  location.  If none exists it'll create a new one.
  """
  CNFG_NAME = 'datamode.info'
  filepath = Path(os.path.join(CONFIG_DIR), CNFG_NAME)

  cfg = configparser.ConfigParser()
  if filepath.is_file():
    try:
      cfg.read(filepath)
    except:
      cfg = init_config()
  else:
    cfg = init_config()
    save_config(cfg, filepath)

  return cfg


def get_auid(ConfigParserObject):
  auid = 'DEFAULT_AUID'

  if 'usage' in ConfigParserObject.sections():
    auid = ConfigParserObject['usage'].get('auid', fallback='DEFAULT_AUID_MISSING_AUID')
  else:
    auid = 'DEFAULT_AUID_INVALID_FORMAT'

  return auid