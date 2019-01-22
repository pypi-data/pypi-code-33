import types

from pymysql import escape_dict, escape_sequence, escape_string

escape_charset = 'utf-8'


def escape(val):
    """
    转义值,防sql注入
    :param val:
    :return:
    """
    if isinstance(val, dict):
        return escape_dict(val, charset=escape_charset)
    elif isinstance(val, (list, set,)):
        return escape_sequence(val, charset=escape_charset)
    else:
        return escape_string(val)


class CastableObject:
    """
    转换对象公共类
    """

    @classmethod
    def parse(clz, exe_result):
        return into_obj(exe_result=exe_result, clz=clz)


def create_cast_obj(kwargs: dict, clz_name: str):
    """
    创造类
    :param kwargs:
    :param clz_name:
    :return:
    """
    class_obj = type(clz_name, (CastableObject,),
                     {})
    for k, v in kwargs.items():
        setter_code = compile(
            'def setter_' + k + '(self,value):' +
            '\n\tself._' + k + ' = value',
            '',
            'exec'
        )
        setter_function_code = [c for c in setter_code.co_consts if isinstance(c, types.CodeType)][0]
        setter_method = types.FunctionType(setter_function_code, {})

        getter_code = compile(
            'def getter_' + k + '(self):' +
            '\n\treturn self._' + k,
            '',
            'exec'
        )
        getter_function_code = [c for c in getter_code.co_consts if isinstance(c, types.CodeType)][0]
        getter_method = types.FunctionType(getter_function_code, {})

        setattr(
            class_obj,
            '_' + k,
            v,
        )

        setattr(
            class_obj,
            k,
            property(getter_method, setter_method)
        )
    return class_obj()


def into_obj(exe_result, clz: CastableObject):
    """
    结果集转换对象
    :param exe_result: 结果集<list,dict>
    :param clz: 转换对象类
    :return:
    """
    if isinstance(exe_result, (list,)):
        return [into_obj_single(item, clz) for item in exe_result]
    elif isinstance(exe_result, (dict,)):
        return into_obj_single(exe_result, clz)
    else:
        raise Exception('实例转换异常')


def into_obj_single(exe_result_item: dict, clz: CastableObject):
    """
    结果集转换对象:单个
    :param exe_result_item: 结果集<dict>
    :param clz: 转换对象类
    :return:
    """
    result_obj = create_cast_obj(exe_result_item, getattr(clz, '__name__'))
    return result_obj

