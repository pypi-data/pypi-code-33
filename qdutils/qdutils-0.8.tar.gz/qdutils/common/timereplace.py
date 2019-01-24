#  -*- coding: utf-8 -*-

'''

@desc: 
@author: tony
@Date: 2018/12/26 下午7:11

'''

import re
import time, re, datetime
from dateutil.relativedelta import relativedelta


class timereplace(object):
    def __init__(self):
        pass

    def DATETIME(self, params, funpar):
        list_funpar = funpar.split(',')
        if len(list_funpar) == 1:
            separate = '-'
        else:
            separate = list_funpar[1]
        format_data = separate.join(['%Y', '%m', '%d'])

        dt_stamp = time.mktime(time.strptime(params['dt'], "%Y-%m-%d"))
        dt_stamp = dt_stamp + (float)(list_funpar[0]) * 86400
        return str(int(dt_stamp))

    def MONTH(self, params, funpar):
        list_funpar = funpar.split(',')
        if len(list_funpar) == 1:
            separate = '-'
        else:
            separate = list_funpar[1]
        delta = list_funpar[0]
        day_f = ['%Y', '%m', '%d']
        month_f = ['%Y', '%m']
        month_res = ''
        try:
            date_struct = datetime.datetime.strptime(params['dt'], '-'.join(day_f))
            date_format = datetime.date(date_struct.year, date_struct.month, date_struct.day)
            month_res = date_format + relativedelta(months=int(delta))
        except Exception, ex:
            print ex
        return datetime.datetime.strftime(month_res, separate.join(month_f))

    def DATE(self, params, funpar):
        list_funpar = funpar.split(',')
        if len(list_funpar) == 1:
            separate = '-'
        else:
            separate = list_funpar[1]
        format_data = separate.join(['%Y', '%m', '%d'])

        dt_stamp = time.mktime(time.strptime(params['dt'], "%Y-%m-%d"))
        return time.strftime(format_data, time.localtime(dt_stamp + (float)(list_funpar[0]) * 86400))

    def HOUR(self, params, funpar):
        list_funpar = funpar.split(',')
        if len(list_funpar) == 1:
            separate = '-'
        else:
            separate = list_funpar[1]

        format_data = '%H'
        join_date = '%s %s:%s' % (str(params['dt']), str(params['hour']), str(params['minute']))
        dt_stamp = time.mktime(time.strptime(join_date, "%Y-%m-%d %H:%M"))
        return time.strftime(format_data, time.localtime(dt_stamp + (float)(list_funpar[0]) * 3600))

    def MINUTE(self, params, funpar):
        list_funpar = funpar.split(',')
        if len(list_funpar) == 1:
            separate = '-'
        else:
            separate = list_funpar[1]

        format_data = '%M'
        join_date = '%s %s:%s' % (str(params['dt']), str(params['hour']), str(params['minute']))
        dt_stamp = time.mktime(time.strptime(join_date, "%Y-%m-%d %H:%M"))
        return time.strftime(format_data, time.localtime(dt_stamp + (float)(list_funpar[0]) * 60))

    def TODAY(self, params, funpar):
        params["dt"] = time.strftime("%Y-%m-%d")

        return self.DATE(params, funpar)

    def NOWTIME(self, params, funpar):
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def date_fun_replace(rs, params):
        """
        :param params: 
        :return: 
        """
        udf = ['DATE|TEST|HOUR|MONTH|DATETIME|MINUTE|NOWTIME']
        reg_udf = '|'.join(udf)
        r = re.compile(r'(\$(%s)\(([-a-zA-Z0-9,_/ ]+)\))' % reg_udf, re.DOTALL)
        result = r.findall(rs)
        obj = timereplace()
        for content in result:
            b = getattr(obj, content[1])
            replace_str = b(params, content[2])
            rs = rs.replace(content[0], replace_str)
        return rs
