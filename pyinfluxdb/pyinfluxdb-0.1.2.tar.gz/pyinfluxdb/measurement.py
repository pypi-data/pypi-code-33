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
    FIND_ONE_BASE = 'SELECT * FROM {condition} ORDER BY time DESC LIMIT 1 tz(\'{timezone}\');'
    FIND_BASE = 'SELECT {select} FROM {condition} ORDER BY time {order} {other} tz(\'{timezone}\');'
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

    def _find(self, select='*', filter=None, desc=True, groupby=None, limit=None, slimit=None, **kwargs):
        condition = '{measurement}'.format(measurement=self.__name)
        if filter is not None:
            condition += ' WHERE ' + filter
        other = ''
        if groupby is not None:
            other += 'GROUP BY {groupby} '.format(groupby=groupby)
        if limit is not None:
            other += 'LIMIT {limit} '.format(limit=limit)
        if slimit is not None:
            other += 'SLIMIT {slimit} '.format(slimit=slimit)

        # other += " tz('{}')".format(self.__timezone)
        sql_str = self.FIND_BASE.format(
            select=select,
            condition=condition,
            order='DESC' if desc else 'ASC',
            other=other,
            timezone=self.__timezone
        )
        logger.debug(sql_str)

        rs = self.__database.query(sql_str)

        return rs

    def find_one(self, filter=None):
        if filter is None:
            filter = dict()
        for k in filter.keys():
            if k in self.key_words:
                raise Exception('key {} is keyword'.format(k))
        kwargs_str_list = ["{} = '{}'".format(k, v) for k, v in filter.items()]
        condition = '{measurement}'.format(measurement=self.__name)
        if kwargs_str_list:
            kwargs_str = ' AND '.join(kwargs_str_list)
            condition += ' WHERE {where}'.format(where=kwargs_str)
        sql_str = self.FIND_ONE_BASE.format(condition=condition, timezone=self.__timezone)
        logger.debug(sql_str)
        rs = self.__database.query(sql_str)
        if rs is None:
            return None
        points = list(rs.get_points(measurement=self.__name))
        if not points:
            return None
        point = points[0]
        # point['time'] = parser.parse(point.get('time', ''))
        return point

    def find(self, filter=None, desc=True, limit=None, slimit=None):
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
            if isinstance(v, datetime):
                value = v.strftime('%Y-%m-%d %H:%M:%S')
                kwargs_str_list.append("{} = '{}'".format(k, value))
                continue
            if isinstance(v, dict):
                for k_f, v_f in v.items():
                    if k_f in ['>', '<', '>=', '<=']:
                        value = v_f
                        if k == 'time':
                            if isinstance(v_f, str):
                                v_f = parser.parse(v_f)
                            value = v_f.strftime('%Y-%m-%d %H:%M:%S')
                        kwargs_str_list.append("{} {} '{}'".format(k, k_f, value))
                continue
        # kwargs_str_list = ["{} = '{}'".format(k, v) for k, v in filter.items()]
        kwargs_str = None
        if kwargs_str_list:
            kwargs_str = ' AND '.join(kwargs_str_list)

        rs = self._find(filter=kwargs_str, desc=desc, limit=limit, slimit=slimit)
        if rs is None:
            return None
        points = list(rs.get_points(measurement=self.__name))
        if not points:
            return []

        # for point in points:
        #     point['time'] = parser.parse(point.get('time', ''))
        return points
