
PJT_NAME = 'inlp'

import os
# 프로젝트 폴더의 상위폴더.
ROOT_PATH = os.environ['ROOT_PATH']
PJT_PATH = f"{ROOT_PATH}/{PJT_NAME}"
PKG_PATH = f"{PJT_PATH}/{PJT_NAME}"
DATA_PATH = f"{PJT_PATH}/data"

#============================================================
# 임시방편 패지키
#============================================================
import sys
LIB_PATH = os.environ['LIB_PATH']
sys.path.append(f"{LIB_PATH}/idebug")
#import idebug as dbg

#============================================================
# Python built-in
#============================================================
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime


#============================================================
# requirements.txt
#============================================================
from pymongo import MongoClient
db = MongoClient()[PJT_NAME]
import pandas as pd

#============================================================
# Modules, Classes, Functions
#============================================================
#from .nltk import *
