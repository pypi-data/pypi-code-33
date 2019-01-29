import os, sys

from datamode.settings import DEFAULT_CONFIG_DIR
from .yamlutils import load_yaml



from .utils import get_logger
log = get_logger(__name__)


import analytics


def on_error(error, items):
  print(f'Error from Segment: {error}')


analytics.write_key = 'O9Ckmdw2rQxMug1zsWWh2AzH2HvccYno'
analytics.on_error = on_error
analytics.debug = False


# Todo: add check for version updates.
# usage_type: quickshow or run_transforms
def send_anonymous_usage(auid, usage_type='NoneSet', transforms=[]):
  if len(transforms) == 0:
    # log.debug('send_anonymous_usage: No transforms selected, bailing.')
    return

  traits = {}
  analytics.identify(auid, traits)

  category = 'Backend'
  transform_names = [transform.__class__.__name__ for transform in transforms]

  analytics.track(auid, f'{usage_type.capitalize()} Executed', {
    'category': category,
    # 'label': usage_type
  })


  for name in transform_names:
    analytics.track(auid, 'Transform Selected', {
      'category': category,
      'label': name,
    })

  # Flush to logs
  sys.stdout.flush()


# Default to True if the setting doesn't exist.
def is_anonymous_tracking_allowed():
  yaml_filepath, yaml_config = load_yaml(DEFAULT_CONFIG_DIR)
  if yaml_config and yaml_config.get('config', None):
    return yaml_config['config'].get('send_anonymous_usage', True)

  return True
