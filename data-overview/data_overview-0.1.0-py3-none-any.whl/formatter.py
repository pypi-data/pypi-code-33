"""该文件对展示项进行格式化
"""


def format_percent(val):
    """格式化：百分比"""
    return '{:2.1f}%'.format(val * 100)


def format_float(val):
    """格式化：float"""
    return str(float('{:.5g}'.format(val))).rstrip('0').rstrip('.')


def format_bytesize(size, suffix='B'):
    """格式化：byte显示方式"""
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < 1024.0:
            return "%3.1f %s%s" % (size, unit, suffix)
        size /= 1024.0
    return "%.1f %s%s" % (size, 'Y', suffix)


var_formatter = {  # 字段类型对应的需要格式化的方式
    'unique_percentage': format_percent,
    'float': format_float
}


def format_value(type, value):
    """对value按照type对应的格式化方式进行格式化"""
    if type in var_formatter:
        return var_formatter[type](value)
    elif isinstance(value, float):
        return var_formatter['float'](value)
    else:
        return str(value)


if __name__ == '__main__':
    import numpy as np
    value = np.NaN
    type = 'date'
    value_formatter = format_value(type, value)
    print(value)
    print(value_formatter)
