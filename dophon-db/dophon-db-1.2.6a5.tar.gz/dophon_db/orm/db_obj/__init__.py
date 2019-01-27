from dophon_db import Connection
from dophon_db import Pool
from dophon_db import utils
import types
from dophon_db.orm.db_obj.type_dict import db_type_python_dict
from dophon_db.orm.db_obj.type_dict import set_check
from dophon_db.orm.db_obj.function_class import *
from dophon_db.orm.query_structor import Struct

from dophon_logger import *

logger = get_logger(DOPHON)

logger.inject_logger(globals())

# 初始化表结构缓存
table_cache = {}


def create_class(table_name: str, table_args: list):
    """
    创建数据表类
    :param table_name:  表名
    :param table_args: 表参数
    :return:
    """
    class_obj = type(table_name, (
        SetAble,
        JoinAble,
        ValueAble,
        Struct,
        Parseable,
        Flushable,
        Pageable),
                     {'__alias': table_name, 'table_map_key': table_name})
    default_arg_list = []
    for table_arg in table_args:
        # 获取表字段名以及属性
        table_arg_field = table_arg['Field']
        table_arg_type = table_arg['Type']
        table_arg_null = table_arg['Null']
        table_arg_key = table_arg['Key']
        table_arg_default = table_arg['Default']

        '''
        映射类属性方法组装
        '''
        setter_code = compile(
            'def setter_' + table_arg_field + '(self,value):' +
            '\n\tself._' + table_arg_field + ' = value' +
            '\n\tself.append(\'' + table_arg_field + '\')',
            '',
            'exec'
        )
        setter_function_code = [c for c in setter_code.co_consts if isinstance(c, types.CodeType)][0]
        setter_method = set_check(table_arg_type)(types.FunctionType(setter_function_code, {}))

        getter_code = compile(
            'def getter_' + table_arg_field + '(self):' +
            '\n\treturn self._' + table_arg_field,
            '',
            'exec'
        )
        getter_function_code = [c for c in getter_code.co_consts if isinstance(c, types.CodeType)][0]
        getter_method = types.FunctionType(getter_function_code, {})

        setattr(
            class_obj,
            '_' + table_arg_field,
            table_arg_default if table_arg_null == 'YES' else None,
        )

        setattr(
            class_obj,
            table_arg_field,
            property(getter_method, setter_method)
        )

        default_arg_list.append(table_arg_field)

    # 设定默认字段列表(所有字段)
    setattr(class_obj, '__default_arg_list', default_arg_list)

    '''
    映射类固定方法组装
    '''
    # 重载直接调用运算符
    callable_code = compile(
        'def __call__(self,call_list):' +
        '\n\treturn self.get_fields(call_list)',
        '',
        'exec'
    )
    callable_function_code = [c for c in callable_code.co_consts if isinstance(c, types.CodeType)][0]
    callable_method = types.FunctionType(callable_function_code, {})

    setattr(
        class_obj,
        '__call__',
        callable_method
    )

    # 重载映射类别名运算符
    alias_code = compile(
        'def alias(self,alias_name:str):' +
        '\n\tself.__alias=alias_name' +
        '\n\treturn self',
        '',
        'exec'
    )
    alias_function_code = [c for c in alias_code.co_consts if isinstance(c, types.CodeType)][0]
    alias_method = types.FunctionType(alias_function_code, {})

    setattr(
        class_obj,
        'alias',
        alias_method
    )

    return class_obj


class OrmManager:
    __table_cache = {}

    def add_orm_obj(self, table_obj: object):
        if 'table_name' in table_obj:
            # 添加表名单位
            table_name = table_obj['table_name']
            table_alias = table_obj['table_alias'] if table_obj['table_alias'] else table_obj['table_name']
            # 编译表名属性方法(property)
            getter_module_code = compile(
                'def ' + table_obj['table_name'] + '(self):\n\treturn self._' + table_obj['table_name'],
                '',
                'exec'
            )
            function_code = [c for c in getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
            getter_method = types.FunctionType(function_code, {})
            # 编译获取管理器连接池方法(property)
            pool_getter_module_code = compile(
                'def pool_getter(self):\n\treturn self.connection_pool',
                '',
                'exec'
            )
            pool_getter_function_code = [c for c in pool_getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
            pool_getter_method = types.FunctionType(pool_getter_function_code, {})
            # 获取表结构
            table_arg = table_obj['table_obj']
            if not search_class_by_name(table_alias):
                # 组装新类
                table_class = create_class(table_name, table_arg)
                save_cache(table_alias, table_class)
            else:
                table_class = get_cache(table_alias)
            # 植入类内
            setattr(OrmManager, '_' + table_name, table_class)
            setattr(OrmManager, table_name, property(getter_method))
            # 植入类内
            setattr(table_class, 'pool_getter', pool_getter_method)
            setattr(table_class, 'connection_pool', self.connection_pool)
            self.__table_cache[table_obj['table_name']] = True
        else:
            logger.error('插入对象异常')
            raise Exception('插入对象异常')

    def has_table(self, table_name: str):
        return table_name in self.__table_cache


def init_pool_in_manager(manager, conn_kwargs):
    """
    初始化对象管理器连接池
    :param manager:
    :param conn_kwargs:
    :return:
    """
    # 组装连接池属相相关
    setattr(manager,'_connection_pool', Pool.get_pool(conn_kwargs))
    # 编译表名属性方法(property)
    getter_module_code = compile(
        'def connection_pool(self):\n\treturn self._connection_pool',
        '',
        'exec'
    )
    function_code = [c for c in getter_module_code.co_consts if isinstance(c, types.CodeType)][0]
    getter_method = types.FunctionType(function_code, {})

    # 植入类内
    setattr(OrmManager, 'connection_pool', property(getter_method))


def init_tables_in_db(manager: OrmManager, tables: list = [], conn_kwargs: dict = {}):
    logger.info('数据库全表ORM初始化开始' if not tables else '数据表' + str(tables[:]) + 'ORM初始化开始')
    connect = Connection.Connection(**conn_kwargs).getConnect()
    cursor = connect.cursor()
    cursor.execute('SHOW TABLES')
    connect.commit()
    # 整理数据表名列表
    for tup_item in cursor.fetchall():
        tup_item_name = tup_item[0]
        if '__host' in conn_kwargs and '__port' in conn_kwargs and '__database' in conn_kwargs:
            tup_item_alias = '-'.join(
                [conn_kwargs.get('__host'), str(conn_kwargs.get('__port')), conn_kwargs.get('__database'), tup_item[0]])
        else:
            tup_item_alias = tup_item_name
        if tables:
            if tup_item_name in tables:
                init_table_param(tup_item_name, manager, table_alias=tup_item_alias, conn_kwargs=conn_kwargs)
        else:
            init_table_param(tup_item_name, manager, table_alias=tup_item_alias, conn_kwargs=conn_kwargs)
    connect.close()
    logger.info('数据库ORM初始化完毕')


def init_table_param(table_name, manager: OrmManager, table_alias: str = '', conn_kwargs: dict = {}):
    connect = Connection.Connection(**conn_kwargs).getConnect()
    cursor = connect.cursor()
    cursor.execute('DESC ' + table_name)
    connect.commit()
    titles = cursor.description
    values = cursor.fetchall()
    result = utils.sort_result(values, titles, [])
    table_obj = {
        'table_alias': table_alias,
        'table_name': table_name,
        'table_obj': result
    }
    manager.add_orm_obj(table_obj)
    connect.close()


def save_cache(table_name: str, table_class: object):
    """
    将orm映射类写入缓存,减少重复创建类
    :param table_class: orm映射类
    :return:
    """
    logger.info('保存映射缓存: %s %s %s', table_name, ' => ', str(table_class))
    table_cache[table_name] = table_class


def get_cache(table_name: str) -> object:
    """
    根据表名获取orm映射类缓存
    :param table_name: 映射表名
    :return: orm映射类
    """
    logger.info('获取映射缓存: %s', table_name)
    return table_cache[table_name]


def search_class_by_name(table_name: str) -> bool:
    """
    根据表名查找缓存
    :param table_name: 映射表名
    :return: 是否命中缓存
    """
    logger.info('检查映射缓存: %s', table_name)
    return table_name in table_cache
