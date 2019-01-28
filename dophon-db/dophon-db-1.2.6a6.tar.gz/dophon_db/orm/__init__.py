from dophon_db.orm.manager_init import *
from dophon_db import properties

from dophon_logger import *

logger = get_logger(DOPHON)

logger.inject_logger(globals())


def init_orm(table_list=[], conn_kwargs={}):
    """
    初始化orm
    :return:
    """
    if hasattr(properties, 'db_cluster'):
        logger.info('分片数据库初始化')
        return ClusterManager()
    else:
        init_orm_manager(table_list, conn_kwargs)
