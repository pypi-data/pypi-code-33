import sqlite3
import types
from dophon_db import properties
from dophon_logger import *

logger = get_logger(DOPHON)

logger.inject_logger(globals())

config = properties.sqlite

cache_config = {}


class Table():
    """
    数据库表类
    """

    def __init__(self, table_structure: set):
        for field in table_structure:
            setattr(self,f'_{field}',None)
            # 获取指定列名数据(property -> get)
            getter_module_code = compile(
                f'@property\ndef {field}(self):\n\treturn self._{field}',
                '',
                'exec'
            )
            gfunction_code = [c for c in getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
            getter_method = types.FunctionType(gfunction_code, {})
            setattr(self, f'{field}', getter_method)
            # 获取指定列名数据(property -> set)
            setter_module_code = compile(
                f'@{field}.setter\ndef set_{field}(self,val):\n\tprint("不可修改的参数")',
                '',
                'exec'
            )
            sfunction_code = [c for c in setter_module_code.co_consts if isinstance(c, types.CodeType)][0]
            setter_method = types.FunctionType(sfunction_code, {})
            setattr(self, f'set_{field}', setter_method)
            setattr(self, field, property(getter_method, setter_method))
        self.__fields = table_structure


class DBObj():
    """
    数据库对象
    """
    __database = ':memory:'

    def __init__(self, database: str = ''):
        self.__database = database if database else self.__database
        # 查询所有的表
        result = self.execute('select name from sqlite_master where type=\'table\' order by name;')
        self.table_fields_struct = {}
        for item in result['data']:
            table_name = item[0]
            # 查询所有表结构
            inner_result = self.execute(f'select * from {table_name};')
            table_fields = set({})
            for table_column in inner_result['desc']:
                table_fields.add(table_column[0])
            self.table_fields_struct[table_name] = table_fields
            setattr(self, f'{table_name}', Table(table_fields))

    def execute(self, sql: str) -> dict:
        """
        执行语句,整理结果集
        :param sql: sql语句
        :return:
        """
        init_conn = sqlite3.connect(self.__database)
        init_cursor = init_conn.cursor()
        init_cursor.execute(sql)
        result = {
            'desc': init_cursor.description,
            'data': init_cursor.fetchall()
        }
        init_conn.commit()
        init_conn.close()
        return result

    def sort_result(self, result: dict):
        """
        整理结果集
        :param result:
        :return:
        """
        dict_result = []
        for result_item in result['data']:
            cache = {result['desc'][index][0]: result_item[index] for index in range(len(result_item))}
            dict_result.append(cache)
        return dict_result


def init_config():
    """
    初始化sqlite配置
    :return:
    """
    if cache_config:
        logger.warning('未生效任何配置')
        return
    for alias_name, alias_config in config.items():
        if isinstance(alias_config, dict):
            cache_config['sqlite_' + alias_name] = DBObj(alias_config['database'])
