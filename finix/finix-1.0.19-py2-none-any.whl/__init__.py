from __future__ import unicode_literals

import wac
import os

__version__ = '1.0.19'
API_ROOT = os.environ.get('PROCESSING_URL')
wac_config = wac.Config(None)
