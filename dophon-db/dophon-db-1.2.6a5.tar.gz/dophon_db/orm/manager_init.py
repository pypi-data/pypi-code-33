from dophon_db.orm import db_obj
from dophon_db.utils import *
from threading import Thread
import time
from hashlib import md5
import re
from dophon_logger import *

logger = get_logger(DOPHON)

logger.inject_logger(globals())

manager_map = {}

singleton_dbm = ''


def init_orm_manager(table_list: list = [], conn_kwargs: dict = {}):
    global manager_map, singleton_dbm
    manager = db_obj.OrmManager()
    # print(conn_kwargs)
    db_obj.init_pool_in_manager(manager,conn_kwargs)
    db_obj.init_tables_in_db(manager, table_list, conn_kwargs)
    if conn_kwargs:
        manager_label = conn_kwargs['alias']
        manager_map[manager_label] = manager
    else:
        singleton_dbm = md5().hexdigest()
    # logger.info(manager_map)
    return manager_map


def init_cluster_orm_manager():
    global manager_map
    if manager_map:
        return manager_map
    db_cluster_info = get_db_cluster_info()
    for cluster_info in db_cluster_info:
        for cluster_name in cluster_info:
            logger.info('初始化分片%s数据库 : %s' % (cluster_name, '::'.join(
                [(str(re.sub('_', '', k)) + '<' + str(v) + '>') for
                 k, v in cluster_info[cluster_name].items() if not re.match('.*(user|password).*', k)]
            ),))
            # orm内部管理器初始化方式启动
            # Thread(target=db_obj.init_tables_in_db, args=(manager,),
            #        kwargs={'conn_kwargs': cluster_info[cluster_name]}).start()
            Thread(target=init_orm_manager,
                   kwargs={
                       'table_list': cluster_info[cluster_name]['table_list'],
                       'conn_kwargs': cluster_info[cluster_name]
                   }).start()
    while len(manager_map) != len(db_cluster_info):
        # print(len(manager_map),'---',len(db_cluster_info))
        time.sleep(1)
    return manager_map


class ClusterManager:
    __map = {}

    def __init__(self):
        self.__map = init_cluster_orm_manager()

    def __getattr__(self, name):
        logger.info('获取相应对象管理')
        result = None
        for k, v in self.__map.items():
            # print(k,'---',v)
            if not result and v.has_table(name):
                result = eval('v.' + name)
        if result:
            return result
        else:
            raise Exception('无法识别的表名')
