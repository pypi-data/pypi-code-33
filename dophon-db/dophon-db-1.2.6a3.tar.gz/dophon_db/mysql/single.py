from dophon_db import properties
from .core import curObj
from dophon_db.mysql import PageHelper
from dophon_db.mysql.remote.Cell import Cell
import re
from dophon_db.const import *
from dophon_logger import *

logger = get_logger(DOPHON)

obj_manager = {}

# 定义项目路径
project_path = properties.project_root


class PageObj(curObj):
    def pageable_exe_sql(self, methodName: str = '', pageInfo: dict = None, args=()) -> dict:
        result_list = self.exe_sql(methodName=methodName, pageInfo=pageInfo, args=args)
        if pageInfo:
            # 获取无分页语句
            un_page_sql = self.get_sql(methodName=methodName, pageInfo=None, args=args)
            if re.match(REGIXSTR.select_sql_check, un_page_sql):
                # sql语句判断(非查询不作分页信息处理)
                un_page_sql = re.sub('^\\s*(s|S)(e|E)(l|L)(e|E)(c|C)(t|T)\\s+.+(f|F)(r|R)(o|O)(m|M)',
                                     'SELECT COUNT(*) FROM',
                                     un_page_sql)
                conn = self._pool.getConn()
                connect = conn.getConnect()
                cursor = connect.cursor()
                cursor.execute(un_page_sql)
                count_items = cursor.fetchall()[0][0]
                connect.commit()
                self._pool.closeConn(conn)
                result = PageHelper.fix_page_info(pageInfo)
                import math
                result['total_page'] = math.ceil(count_items / result['page_size'])
                result['list'] = result_list
                return result
        return result_list


def getDbObj(path, debug: bool = False, auto_fix: bool = False):
    """
    获取数据表实例
    :param path: xml文件路径
    :param debug: 是否开启调试模式
    :param auto_fix: 是否开启路径修复模式(损耗资源) <===  待测试
    :return: xml对应实例
    """
    # if not pool:
    #     logger.error('连接池未定义')
    #     raise Exception('连接池未定义')
    # if 0 >= pool.size():
    #     配置属性生命周期过短,拟用__import__导入减轻内存废址
        # prop = __import__('properties')
        # if hasattr(prop, 'pool_conn_num'):
        #     pool.initPool(getattr(prop, 'pool_conn_num'), Connection.Connection)
        # else:
        #     初始5个连接
            # pool.initPool(5, Connection.Connection)
    if isinstance(path, str):
        if auto_fix:
            pattern = re.sub(r'\\', r'\\\\', re.sub('/', '\\/', project_path))
            if not re.search(pattern, path):
                r_path = str(project_path) + str(path)
            else:
                r_path = str(path)
        else:
            r_path = path
    elif isinstance(path, Cell):
        r_path = path.getPath()
    else:
        raise TypeError('结果集路径类型错误')
    # 数据语句对象改为单例模式获取
    if r_path in obj_manager:
        return obj_manager[r_path]
    singleton_obj = curObj(r_path, True, debug)
    obj_manager[r_path] = singleton_obj
    return singleton_obj


def getPgObj(path, debug: bool = False, auto_fix: bool = False):
    """
    获取数据表实例
    :param path: xml文件路径
    :param debug: 是否开启调试模式
    :param auto_fix: 是否开启路径修复模式(损耗资源) <===  待测试
    :return: xml对应实例
    """
    # if pool is None:
    #     logger.error('连接池未定义')
    #     raise Exception('连接池未定义')
    # if 0 >= pool.size():
        # 配置属性生命周期过短,拟用__import__导入减轻内存废址
        # prop = __import__('properties')
        # if hasattr(prop, 'pool_conn_num'):
        #     pool.initPool(getattr(prop, 'pool_conn_num'), Connection.Connection)
        # else:
            # 初始5个连接
            # pool.initPool(5, Connection.Connection)
    if isinstance(path, str):
        if auto_fix:
            pattern = re.sub(r'\\', r'\\\\', re.sub('/', '\\/', project_path))
            if not re.search(pattern, path):
                r_path = str(project_path) + str(path)
            else:
                r_path = str(path)
        else:
            r_path = path
    elif isinstance(path, Cell):
        r_path = path.getPath()
    else:
        raise TypeError('结果集路径类型错误')
    # 数据语句对象改为单例模式获取
    if r_path in obj_manager:
        return obj_manager[r_path]
    singleton_obj = PageObj(r_path, True, debug)
    obj_manager[r_path] = singleton_obj
    return singleton_obj

