"""
缓存相关的操作
"""
import requests
from munch import Munch

from client import ClientAuth
from client.FicusServerGetter import ficusServerGetter
from api.exceptions import ServiceNoInstanceException, ServiceInnerException, AuthException


def set_value(key, value):
    """
    设置缓存值
    :param key:
    :param value:
    :return:
    """
    if key is None or value is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = value
    if not isinstance(value, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(value, dict):
            # 如果是dict类型的,直接发
            request = value
    else:
        # 说明是munch的,那么就转成Dict的
        request = value.toDict()

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/sc-service/{key}", json=request,auth=ClientAuth())
        r.raise_for_status()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        set_value(key, value)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def set_if_absent(key, value):
    """
    设置缓存自,如果key不存在
    :param key:
    :param value:
    :return:
    """
    if key is None or value is None:
        return False

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = None
    if not isinstance(value, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(value, dict):
            # 如果是dict类型的,直接发
            request = value
    else:
        # 说明是munch的,那么就转成Dict的
        request = value.toDict()

    try:
        r = requests.put(f"{ficusServerGetter.server_url}remote/sc-service/{key}", json=request,auth=ClientAuth())
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return set_if_absent(key, value)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def get(key):
    """
    获取某一个缓存
    :param key:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/sc-service/{key}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            try:
                return Munch(r.json())
            except TypeError:
                return r.json()
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return get(key)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def delete(key):
    """
    删除某一个缓存
    :param key:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.delete(f"{ficusServerGetter.server_url}remote/sc-service/{key}",auth=ClientAuth())
        r.raise_for_status()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        delete(key)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
