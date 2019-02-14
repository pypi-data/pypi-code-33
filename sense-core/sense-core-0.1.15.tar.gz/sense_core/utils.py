import numpy
import json
import datetime
import time
from dateutil import parser
import re
import shortuuid


def dump_json(data):
    return json.dumps(data, ensure_ascii=False)


def load_json(data):
    try:
        return json.loads(data)
    except:
        return None


def sleep(seconds):
    time.sleep(seconds)


def parse_date(str):
    return parser.parse(str)


def timestamp_to_str(time1, format='%Y-%m-%d'):
    return datetime.datetime.fromtimestamp(time1).strftime(format)


def get_current_millisecond():
    return int(round(time.time() * 1000))


def get_current_second():
    return int(round(time.time()))


def format_time_cost(val):
    result = ''
    if val >= 3600:
        hour = int(val / 3600)
        result += str(hour) + '小时'
        val -= hour * 3600
    if val >= 60:
        min = int(val / 60)
        result += str(min) + '分'
        val -= min * 60
    result += str(val) + '秒'
    return result


def format_blank(content):
    clear_list = {
        u'\u2002': '', u'\u2003': '', u'\u2009': '', u'\u200c\u200d': '', u'\xa0': '', '&nbsp;': '',
        '&ensp;': '', '&emsp;': '', '&zwj;': '', '&zwnj;': ''
    }
    rep = dict((re.escape(k), v) for k, v in clear_list.items())
    pattern = re.compile('|'.join(rep.keys()))
    content = pattern.sub(lambda x: rep[re.escape(x.group(0))], content)
    return content


def get_url_uuid(url):
    return shortuuid.uuid(name=url)


class TimeCost(object):
    __start = get_current_second()

    @classmethod
    def show_time_diff(cls):
        return format_time_cost(get_current_second() - cls.__start)

    @classmethod
    def reset_time(cls):
        cls.__start = get_current_second()
