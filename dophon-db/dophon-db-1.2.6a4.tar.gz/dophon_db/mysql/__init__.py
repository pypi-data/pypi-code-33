from dophon_db import properties
from .core import *
from .core import CurObj
from . import cluster_manager
from dophon_db.mysql import PageHelper
from dophon_db.mysql.remote.Cell import Cell
from dophon_db.mysql import binlog
from dophon_db.mysql.binlog import Schued
from dophon_db.mysql.sql_util import *
from dophon_logger import *

logger = get_logger(DOPHON)

ALL = -1
SINGLE = 0
CLUSTER = 1

# 默认优先模式是分片
priority_mode = properties.db_mode if isinstance(properties.db_mode, int) else eval(properties.db_mode)

db_cluster = cluster_manager.get_db

from .single import getDbObj, getPgObj

db_obj = None
pg_obj = None


def assert_single():
    return (db_obj if priority_mode == SINGLE or priority_mode == ALL else True) \
           and \
           (pg_obj if priority_mode == SINGLE or priority_mode == ALL else True)


def assert_cluster():
    return db_cluster if priority_mode == CLUSTER or priority_mode == ALL else True


def mode_assert(mode_type: str):
    def fun(f):
        def arg_bucket(*args, **kwargs):
            assert priority_mode == eval(mode_type) or priority_mode == ALL, f'模式异常,请切换至({mode_type})或(ALL)'
            return f(*args, **kwargs)

        return arg_bucket

    return fun


if priority_mode == CLUSTER:
    cluster_manager.init_cluster_manager()
    # assert assert_cluster(), f'未切换到使用多源模式,当前模式为(SINGLE)'
if priority_mode == SINGLE:
    db_obj = mode_assert('SINGLE')(getDbObj)
    pg_obj = mode_assert('SINGLE')(getPgObj)
    # assert assert_single(), f'未切换到使用单源模式,当前模式为(CLUSTER)'
if priority_mode == ALL:
    cluster_manager.init_cluster_manager()
    db_obj = mode_assert('SINGLE')(getDbObj)
    pg_obj = mode_assert('SINGLE')(getPgObj)
    # assert assert_cluster(), f'未切换到使用多源模式,当前模式为(SINGLE)'
    # assert assert_single(), f'未切换到使用单源模式,当前模式为(CLUSTER)'

__all__ = ['db_obj', 'pg_obj', 'db_cluster']
