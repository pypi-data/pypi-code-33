"""
schedule相关的操作
"""
import requests
from munch import Munch

from client import ClientAuth
from client.FicusServerGetter import ficusServerGetter
from api.exceptions import ServiceNoInstanceException, ServiceInnerException, AuthException


def add_job(job_info):
    """
    新增计划
    :param job_info: jobInfo对象
    :return: 如果成功返回True,否则返回False
    """
    if job_info is None:
        return False

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = None
    if not isinstance(job_info, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(job_info, dict):
            # 如果是dict类型的,直接发
            request = job_info
    else:
        # 说明是munch的,那么就转成Dict的
        request = job_info.toDict()

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/js-service/", json=request,auth=ClientAuth())
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return add_job(job_info)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def reschedule(job_info):
    """
    更新计划
    :param job_info:
    :return:
    """
    if job_info is None:
        return False

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = None
    if not isinstance(job_info, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(job_info, dict):
            # 如果是dict类型的,直接发
            request = job_info
    else:
        # 说明是munch的,那么就转成Dict的
        request = job_info.toDict()

    try:
        r = requests.put(f"{ficusServerGetter.server_url}remote/js-service/", json=request,auth=ClientAuth())
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return reschedule(job_info)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def remove(job_id):
    """
    删除一个计划
    :param job_id:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.delete(f"{ficusServerGetter.server_url}remote/js-service/{job_id}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return False
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return remove(job_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def pause(job_id):
    """
    暂停计划
    :param job_id:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/js-service/{job_id}/pause",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return False
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return pause(job_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def resume(job_id):
    """
    恢复计划
    :param job_id:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/js-service/{job_id}/resume",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return False
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return resume(job_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def stop(job_id):
    """
    停止计划
    :param job_id:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/js-service/{job_id}/stop",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return False
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return stop(job_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def trigger_job(job_id, params=None):
    """
    触发一个计划
    :param job_id:
    :param params:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/js-service/{job_id}/trigger", json=params,auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return False
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return trigger_job(job_id, params)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def list_jobs():
    """
    列出所有的计划
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/js-service",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            ll = r.json()
            if isinstance(ll, list):
                return [Munch(x) for x in ll]
            else:
                return Munch(ll)
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return list_jobs()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def get_jobs(actor_name):
    """
    找到某一个类型的所有计划
    :param actor_name:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/js-service/{actor_name}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            ll = r.json()
            if isinstance(ll, list):
                return [Munch(x) for x in ll]
            else:
                return Munch(ll)
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return get_jobs(actor_name)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def find_by_site_and_code(site, project_code, code):
    """
    返回某一个计划
    :param site:
    :param project_code:
    :param code:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/js-service/{site}/{project_code}/{code}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return Munch(r.json())
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return find_by_site_and_code(site, project_code, code)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
