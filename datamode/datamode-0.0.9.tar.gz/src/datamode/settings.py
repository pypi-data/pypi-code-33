import os, logging, logging.config

from .utils.exceptionutils import setup_custom_excepthook, enable_http_tracing
from .utils.logutils import COLOR_FORMAT, COLOR_FORMAT_DEV
from .utils.utils import DATETIME_FMT
from .utils.notebook import in_ipynb
from .utils.utils import ensure_dir
from .utils.cfgutils import get_auid, load_config

launch_ipdb = bool( int(os.getenv('LAUNCH_IPDB', 0)) )

###
### Datamode Config Dir
###
# Relying on os.path.expanduser() to play nice with unix and windows
# https://docs.python.org/3/library/os.path.html#os.path.expanduser
DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.datamode')
CONFIG_DIR = os.environ.get('DATAMODE_CONFIG_DIR', DEFAULT_CONFIG_DIR)
ensure_dir(CONFIG_DIR)


###
### Datamode Config
###
DATAMODE_CONFIG = load_config(CONFIG_DIR)
AUID = get_auid(DATAMODE_CONFIG)

# Settings
LAUNCH_IPDB = launch_ipdb
ENABLE_HTTP_TRACING = False
IN_IPYNB = in_ipynb()
DEBUG = True

###
### Logging
###

# Use COLOR_FORMAT_DEV for a shorter format that omits timestamps and the logging source module.
# Use COLOR_FORMAT for production code.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': True,
  'formatters': {
    'standard': {
      'format': COLOR_FORMAT_DEV,
      'datefmt': DATETIME_FMT,
      'class': 'datamode.utils.logutils.ColoredFormatter',
    }
  },
  # Config spec is at https://docs.python.org/3/library/logging.html#logging.basicConfig
  'handlers': {
    'console': {
      'level': 'DEBUG',
      'formatter': 'standard',
      'class': 'logging.StreamHandler',
      'stream': 'ext://sys.stdout',  # Send all logs to stdout (not split between stdout/stderr)
    },
    'notebook': {
      'level': 'DEBUG',
      'formatter': 'standard',
      'class': 'datamode.utils.logutils.MarkdownHandler',
      'stream': 'ext://sys.stdout',  # Send all logs to stdout (not split between stdout/stderr)
    },
    'file': {
      'level': 'DEBUG',
      'formatter': 'standard',
      'class': 'logging.FileHandler',
      'filename': '{0}'.format(os.path.join(CONFIG_DIR, 'datamode.log')),
    },
  },
  'loggers': {
    # '': {
    #   'handlers': ['console'],
    #   'level': 'ERROR',
    #   'propagate': False,
    # },

    # Prefix that will appear in the log, e.g. 'datamode.main'
    'datamode': {
      'handlers': ['notebook' if IN_IPYNB else 'console', 'file'],
      'level':'DEBUG',
      'propagate': False,
    },
  }
}

###
### Utils/monkeypatching
###
### Has to be after the prod settings import, so that has a chance to override logging settings.
###

# Setup exception hook if desired

if DEBUG:
  setup_custom_excepthook(launch_ipdb=LAUNCH_IPDB)

if ENABLE_HTTP_TRACING:
  enable_http_tracing()

# Note: if you turn this on, you won't see exceptions in the Jupyter webserver (e.g. for comms)
logging.config.dictConfig(LOGGING)

# Turn off matplotlib debug logs
logger_matplotlib = logging.getLogger('matplotlib')
logger_matplotlib.setLevel(logging.WARNING)
