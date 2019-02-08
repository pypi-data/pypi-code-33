
PJT_NAME = 'igoogle'

import os
ROOT_PATH = os.environ['ROOT_PATH']
PJT_PATH = f"{ROOT_PATH}/{PJT_NAME}"
DATA_PATH = f"{ROOT_PATH}/{PJT_NAME}/data"

import sys
sys.path.append(PJT_PATH)
from igoogle import *
