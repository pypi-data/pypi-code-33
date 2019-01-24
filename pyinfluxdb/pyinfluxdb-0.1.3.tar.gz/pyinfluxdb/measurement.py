"""
@Time    : 2019/1/16 17:32
@Author  : Sam
@Project : pyinfluxdb
@FileName: measurement.py
@Software: PyCharm
@Blog    : https://blog.muumlover.com
"""
import logging
from datetime import datetime

from dateutil import parser

logger = logging.getLogger(__name__)


class Measurement(object):
    # FIND_ONE_BASE = 'SELECT * FROM {name} {condition} ORDER BY time DESC LIMIT 1 tz(\'{timezone}\');'
    # FIND_BASE = 'SELECT {select} FROM {name} {condition} ORDER BY time {order} {other} tz(\'{timezone}\');'
    # 'SELECT * FROM {condition} ORDER BY time DESC tz(\'{timezone}\');'
    key_words = ['name', 'key']

    def __init__(self, database, name, timezone):
        if not isinstance(name, str):
            raise TypeError("name must be an instance "
                            "of %s" % (str.__name__,))

        if not name or ".." in name:
            raise Exception("collection names cannot be empty")
        if "$" in name and not (name.startswith("oplog.$main") or
                                name.startswith("$cmd")):
            raise Exception("collection names must not "
                            "contain '$': %r" % name)
        if name[0] == "." or name[-1] == ".":
            raise Exception("collection names must not start "
                            "or end with '.': %r" % name)
        if "\x00" in name:
            raise Exception("collection names must not contain the "
                            "null character")

        self.__database = database
        self.__name = name
        self.__timezone = timezone

    def insert_one(self, tags, fields):
        point = dict(
            fields=fields,
            tags=tags,
            measurement=self.__name
        )
        return self.__database.write_points([point])

    def _query_exec(self,
                    f_select,
                    f_from,
                    f_where=None,
                    f_aggregate=None,
                    f_group_by=None,
                    f_group_time=None,
                    f_group_fill=None,
                    f_order_by=None,
                    f_order_desc=None,
                    f_limit=None,
                    f_offset=None,
                    f_slimit=None,
                    f_soffset=None,
                    timezone=None,
                    **kwargs):
        """
        SELECT_clause [INTO_clause] FROM_clause [WHERE_clause] [GROUP_BY_clause] [ORDER_BY_clause]

        SELECT_clause:
            SELECT *
            SELECT "<field_key>"
            SELECT "<field_key>","<field_key>"
            SELECT "<field_key>","<tag_key>"

        FROM_clause:
            FROM <measurement_name>
            FROM <measurement_name>,<measurement_name>
            FROM <database_name>.<retention_policy_name>.<measurement_name>
            FROM <database_name>..<measurement_name>

        WHERE_clause:
            WHERE <conditional_expression> [(AND|OR) <conditional_expression> [...]]
                <conditional_expression>
                WHERE field_key <operator> ['string' | boolean | float | integer]
                WHERE tag_key <operator> ['tag_value']

        GROUP_BY_clause:
            GROUP BY *
            GROUP BY <tag_key>
            GROUP BY <tag_key>,<tag_key>

        ORDER_BY_clause:
            ORDER BY time DESC

        :param f_select:
        :param f_from:
        :param f_where:
        :param f_group_by:
        :type f_group_fill: FILL
        :param f_group_fill:
        :param f_order_by:
        :param f_order_desc:
        :param f_limit:
        :param f_offset:
        :param f_slimit:
        :param f_soffset:
        :param kwargs:
        :return:
        """
        if f_group_time or f_group_fill:
            if not f_group_by or f_group_by != 'time':
                raise Exception('f_group_by is not set to time')

        sql_list = list()
        if f_select:
            sql_list.append('SELECT')
            if f_aggregate:
                sql_list.append(str(f'{f_aggregate}("{f_select}")'))
            else:
                sql_list.append(str(f_select))
        if f_from:
            sql_list.append('FROM')
            sql_list.append(str(f_from))
        if f_where:
            sql_list.append('WHERE')
            sql_list.append(str(f_where))

        if f_group_by:
            sql_list.append('GROUP BY')
            if f_group_by != 'time':
                sql_list.append(str(f_group_by))
            else:
                if not f_group_time:
                    raise Exception('f_group_time is need set')
                sql_list.append(str(f'time({f_group_time})'))
                if f_group_fill:
                    sql_list.append(f'fill({f_group_fill})')

        if f_order_by:
            sql_list.append('ORDER BY')
            sql_list.append(str(f_order_by))
            sql_list.append(str('DESC' if f_order_desc else 'ASC'))

        if f_limit:
            sql_list.append('LIMIT')
            sql_list.append(str(f_limit))

        if f_slimit:
            sql_list.append('SLIMIT')
            sql_list.append(str(f_slimit))
        if timezone:
            sql_list.append(f'tz(\'{timezone}\')')
        sql_str = ' '.join(sql_list)
        logger.debug(sql_str)
        rs = self.__database.query(sql_str)
        return rs

    def _conditional_expression(self, filter):
        if filter is None:
            filter = dict()
        kwargs_str_list = list()
        for k, v in filter.items():
            if k in self.key_words:
                raise Exception('key {} is keyword'.format(k))
            if isinstance(v, str):
                value = v
                if k == 'time':
                    t = parser.parse(v)
                    value = t.strftime('%Y-%m-%d %H:%M:%S')
                kwargs_str_list.append("{} = '{}'".format(k, value))
                continue
            elif isinstance(v, datetime):
                value = v.strftime('%Y-%m-%d %H:%M:%S')
                kwargs_str_list.append("{} = '{}'".format(k, value))
                continue
            elif isinstance(v, dict):
                for k_f, v_f in v.items():
                    if k_f in ['=', '<>', '!=', '>', '>=', '<', '<=']:
                        value = v_f
                        if k == 'time':
                            if isinstance(v_f, str):
                                v_f = parser.parse(v_f)
                            value = v_f.strftime('%Y-%m-%d %H:%M:%S')
                        kwargs_str_list.append("{} {} '{}'".format(k, k_f, value))
                continue
            else:
                value = v
                kwargs_str_list.append("{} = '{}'".format(k, value))
        # kwargs_str_list = ["{} = '{}'".format(k, v) for k, v in filter.items()]
        kwargs_str = None
        if kwargs_str_list:
            kwargs_str = ' AND '.join(kwargs_str_list)
        return kwargs_str

    def find_one(self, filter=None):
        f_where = self._conditional_expression(filter)
        rs = self._query_exec(
            f_select='*',
            f_from=self.__name,
            f_where=f_where,
            f_order_by='time',  # 按时间排序
            f_order_desc=True,  # 最新的条目在前
            f_limit=1,  # 取最前面的一条
            timezone=self.__timezone)
        if rs is None:
            return None
        point_iter = rs.get_points(measurement=self.__name)
        try:
            point = point_iter.__next__()
        except StopIteration:
            point = None
        return point

    def find(self, filter=None, desc=True, limit=None):
        f_where = self._conditional_expression(filter)
        rs = self._query_exec(
            f_select='*',
            f_from=self.__name,
            f_where=f_where,
            f_order_by='time',
            f_order_desc=desc,
            f_limit=limit,
            timezone=self.__timezone)
        if rs is None:
            return []
        points = list(rs.get_points(measurement=self.__name))
        return points

    def aggregate(self, aggregate, filter, fields, time_span, fill_type):
        """
        :type aggregate: object
        :type filter: object
        :type fields: object
        :type time_span: object
        :type fill_type: FILL

        """
        f_where = self._conditional_expression(filter)
        rs = self._query_exec(
            f_select=fields,
            f_from=self.__name,
            f_where=f_where,
            f_aggregate=aggregate,
            f_group_by='time',
            f_group_time=time_span,
            f_group_fill=fill_type,
            # f_order_by='time',
            # f_order_desc=False,
            timezone=self.__timezone)
        if rs is None:
            return []
        points = list(rs.get_points(measurement=self.__name))
        return points
        pass
    #
    # def bottom(self, *args, **kwargs):
    #     return self.aggregate(aggregate='BOTTOM', *args, **kwargs)
    #
    # def first(self, *args, **kwargs):
    #     return self.aggregate(aggregate='FIRST', *args, **kwargs)
    #
    # def last(self, *args, **kwargs):
    #     return self.aggregate(aggregate='LAST', *args, **kwargs)
    #
    # def max(self, *args, **kwargs):
    #     return self.aggregate(aggregate='MAX', *args, **kwargs)
    #
    # def min(self, *args, **kwargs):
    #     return self.aggregate(aggregate='MIN', *args, **kwargs)
    #
    # def percentile(self, *args, **kwargs):
    #     return self.aggregate(aggregate='PERCENTILE', *args, **kwargs)
    #
    # def sample(self, *args, **kwargs):
    #     return self.aggregate(aggregate='SAMPLE', *args, **kwargs)
    #
    # def top(self, *args, **kwargs):
    #     return self.aggregate(aggregate='TOP', *args, **kwargs)

    aggregate_list = ['bottom', 'first', 'last', 'max', 'min', 'percentile', 'sample', 'top']

    def __getattr__(self, item):
        if item in self.aggregate_list:
            return lambda *args, **kwargs: self.aggregate(aggregate=item.upper(), *args, **kwargs)
        else:
            return super().__getattr__(self, item)
