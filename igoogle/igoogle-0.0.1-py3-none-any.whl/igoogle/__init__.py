
PJT_NAME = 'google'

import os
# 프로젝트 폴더의 상위폴더.
ROOT_PATH = os.environ['ROOT_PATH']
PJT_PATH = f"{ROOT_PATH}/{PJT_NAME}"
DATA_PATH = f"{ROOT_PATH}/{PJT_NAME}/data"
import sys
sys.path.append(PJT_PATH)

GOOGLE_AUTH_PATH = os.environ['GOOGLE_AUTH_PATH']
CLIENT_SECRET_FILE = f"{GOOGLE_AUTH_PATH}/client_secret.json"

#============================================================
# 임시방편 패지키
#============================================================
LIB_PATH = os.environ['LIB_PATH']

#============================================================
# Python built-iin
#============================================================
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime

#============================================================
# requirements.txt
#============================================================
import pandas as pd

#============================================================
# Modules, Classes, Functions
#============================================================
