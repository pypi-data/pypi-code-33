import math
from dophon_db import utils

from dophon_logger import *

logger = get_logger(DOPHON)

"""
查询语句结构映射

结构:
select
<Field>
from
<tables>
where
<param_dicts>
<sort_param>
"""

logger.inject_logger(globals())


def get_connection(target):
    """
    从连接池中获取连接
    :return:
    """
    return target.pool_getter().getConn()


class Selelct:
    """
    查询结构类
    """

    def before_select(self, fields_list: list, has_where: bool) -> str:
        result = f"""SELECT {(getattr(self, 'fields')(fields_list) if fields_list else ' * ')} FROM """f"""{(
            getattr(self, 'table_map_key') + ((' AS ' + getattr(self, '__alias'))
                                              if getattr(self, '__alias') != getattr(self, 'table_map_key') else '')
            if not hasattr(self, '__join_list') else (getattr(self, 'exe_join')()))}{(
            getattr(self, 'where')() if has_where else '')} {getattr(self, '__execuable_limit_sql')
        if hasattr(self, '__execuable_limit_sql') and hasattr(self, '__limit_start') else ''}"""
        return result.replace('\n', ' ')

    def select(self, fields: list = [], has_where: bool = True) -> list:
        """
        查询并获取该表结果集
        :param fields: 列参
        :return: <list> 多条结果列表
        """
        sql = self.before_select(fields, has_where)
        logger.info('执行: %s', sql)
        result = []
        connection = get_connection(self)
        cursor = connection.cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        connection.commit()
        result = utils.sort_result(data, description, result)
        # 清除当前分页信息
        if hasattr(self, '__execuable_limit_sql') and hasattr(self, '__limit_start'):
            self.clear_limit_info()
        return self.page_filter(result) if getattr(self, '__page_switch', False) else result

    def select_one(self, fields: list = []) -> dict:
        """
        查询一条结果集
        :param fields: 列参
        :return: <dict> 单条结果集字典
        """
        if hasattr(self, '__field_callable_list') and len(getattr(self, '__field_callable_list')) > 0:
            # 存在可生成的查询条件
            result = self.select(fields=fields)
            assert len(result) > -1, '神奇的错误'
            assert len(result) == 1, '过多结果集'
            return self.page_filter(result) if getattr(self, '__page_switch', False) else result
        else:
            logger.error('无法预料的唯一结果集,找不到查询过滤条件')
            raise Exception('无法预料的唯一结果集,找不到查询过滤条件')

    def select_all(self, fields: list = [], ignore_fields_warning: bool = True) -> list:
        """
        同select
        :param fields:
        :return:
        """
        if not ignore_fields_warning and hasattr(self, '__field_callable_list') and len(
                getattr(self, '__field_callable_list')) > 0:
            logger.warning('警告:存在查询过滤条件 %s ', str(getattr(self, '__field_callable_list')))
        result = self.select(fields=fields, has_where=False)
        return self.page_filter(result) if getattr(self, '__page_switch', False) else result

    def before_count(self, field_name: str, has_where: bool) -> str:
        count_str = getattr(self, 'fields')([field_name]) if field_name else ' * '
        assert count_str, '无此列名'
        result = f"""SELECT COUNT({count_str}) AS count FROM """f"""{(
            getattr(self, 'table_map_key') + ((' AS ' + getattr(self, '__alias'))
                                              if getattr(self, '__alias') != getattr(self, 'table_map_key') else '')
            if not hasattr(self, '__join_list') else (getattr(self, 'exe_join')()))}{(
            getattr(self, 'where')() if has_where else '')} {getattr(self, '__execuable_limit_sql')
        if hasattr(self, '__execuable_limit_sql') and hasattr(self, '__limit_start') else ''}"""
        return result.replace('\n', ' ')

    def count(self, field: str = '', has_where: bool = True):
        """
        查询条数
        :return:
        """
        sql = self.before_count(field, has_where)
        logger.info('执行: %s', sql)
        result = []
        connection = get_connection(self)
        cursor = connection.cursor()
        cursor.execute(sql)
        if not sql.startswith('select') and not sql.startswith('SELECT'):
            data = [[cursor.rowcount]]
            description = [['row_count']]
        else:
            data = cursor.fetchall()
            description = cursor.description
        connection.commit()
        result = utils.sort_result(data, description, result)[0]
        return result

    def page_filter(self, result: list) -> dict:
        """
        分页过滤器

        注意: pages值由于python3问题为一个可迭代对象
        :param result:
        :return:
        """
        c_num = int(self.count()['count'])
        page_size = getattr(self, '__page_size', -1)
        pages_size = getattr(self, '__pages_size')
        page_num = getattr(self, '__page_num', 0)
        assert page_size > -1, '不存在分页信息'
        total_page = math.ceil((c_num / page_size))
        # 清除分页信息
        self.clear_page_info()
        return {
            'list': result if isinstance(result, list) else [result],
            'total': c_num,
            'total_page': total_page,
            'pages': list(
                range(page_num, (total_page if total_page <= (page_num + pages_size) else (page_num + pages_size)))
            )
        }


class Insert:
    """
    新增结构类
    """

    def before_insert(self):
        result = 'INSERT INTO ' + \
                 getattr(self, 'table_map_key') + ' ' + \
                 getattr(self, 'values')()
        return result

    def insert(self) -> int:
        """
        新增结果集
        :return: <int> 影响行数
                [{'row_count': '0'}]
        """
        sql = self.before_insert()
        logger.info('执行: %s', sql)
        result = []
        connection = get_connection(self)
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            if not sql.startswith('select') and not sql.startswith('SELECT'):
                data = [[cursor.rowcount]]
                description = [['row_count']]
            else:
                data = cursor.fetchall()
                description = cursor.description
            connection.commit()
            result = utils.sort_result(data, description, result)[0]['row_count']
            return int(result)
        except Exception as e:
            logger.error('%s', e)
            connection.rollback()
            return 0


class Update():
    """
    更新结构类
    """

    def before_update(self, update: list, where: list):
        result = 'UPDATE ' + getattr(self, 'table_map_key') + \
                 (
                     (' AS ' + getattr(self, '__alias'))
                     if getattr(self, '__alias') != getattr(self, 'table_map_key') else ''
                 ) + \
                 getattr(self, 'set')(update) + \
                 getattr(self, 'where')(where)
        return result

    def update(self, update: list = [], where: list = []) -> int:
        """
        更新结果集
        :param update: 更新列参
        :param where: 条件列参
        :return: <int> 影响行数
        """
        sql = self.before_update(update, where)
        logger.info('执行: %s', sql)
        result = []
        connection = get_connection(self)
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            if not sql.startswith('select') and not sql.startswith('SELECT'):
                data = [[cursor.rowcount]]
                description = [['row_count']]
            else:
                data = cursor.fetchall()
                description = cursor.description
            connection.commit()
            result = utils.sort_result(data, description, result)[0]['row_count']
            return int(result)
        except Exception as e:
            logger.error('%s', e)
            connection.rollback()
            return 0


class Delete():
    """
    删除结构类
    """

    def before_delete(self, where: list):
        result = 'DELETE FROM ' + getattr(self, 'table_map_key') + \
                 ' ' + getattr(self, 'where')(where, be_alias=False)
        return result

    def delete(self, where: list = []) -> int:
        """
        删除结果集

        :param where: 条件列参
        :return: <int> 影响行数
        """
        sql = self.before_delete(where)
        logger.info('执行: %s', sql)
        result = []
        connection = get_connection(self)
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            if not sql.startswith('select') and not sql.startswith('SELECT'):
                data = [[cursor.rowcount]]
                description = [['row_count']]
            else:
                data = cursor.fetchall()
                description = cursor.description
            connection.commit()
            result = utils.sort_result(data, description, result)[0]['row_count']
            return int(result)
        except Exception as e:
            logger.error('%s', e)
            connection.rollback()
            return 0


class Struct(Selelct, Insert, Update, Delete):
    """
    查询语句结构类
    """
