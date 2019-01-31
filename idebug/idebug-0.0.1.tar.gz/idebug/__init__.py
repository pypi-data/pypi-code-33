"""
============================== 핵심일 ==============================
debug 모듈에 있는 모든 함수는 기본적으로 dbgon 파라미터를 받지 않는다.
왜냐하면 디버그 용이기 때문에 모든 로그를 찍어야 하기 때문이다.
파라미터를 받는다는 것은, 사용자가 결정권을 가질 수 있다는 뜻인데,
이 모듈에서 결정하지 말고, 서비스 모듈/함수에서 결정해서 이 모듈을 호출하도록 한다.
단, 예외적으로 "함수실행로그" 는 허용한다.
"""
PJT_NAME = 'ilibs'
PKG_NAME = 'idbg'
import os
ROOT_PATH = os.environ['PJTS_PATH']
PJT_PATH = f"{ROOT_PATH}/{PJT_NAME}"
DATA_PATH = f"{PJT_PATH}/data"

import sys
sys.path.append(PJT_PATH)
import ilist as lh
import inumber

import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
db = MongoClient()[PKG_NAME]
import json

from .dbg import *
