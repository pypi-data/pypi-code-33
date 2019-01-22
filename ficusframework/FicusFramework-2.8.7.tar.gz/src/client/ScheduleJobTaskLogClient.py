"""
任务记录相关的操作
"""
from datetime import datetime

import requests
from munch import Munch

from client import ClientAuth
from client.FicusServerGetter import ficusServerGetter
from api.exceptions import ServiceNoInstanceException, ServiceInnerException, AuthException


def update_task_status_to_execute(log_id, instance_address):
    """
    更新任务的状态到正在执行
    :param log_id:
    :param instance_address:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/sjtl-service/{log_id}/execute",
                          params={'instanceAddress': instance_address},auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return Munch(r.json())
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return update_task_status_to_execute(log_id, instance_address)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def update_task_status_to_finished(log_id, execute_result,triggerProcess):
    """
    更新任务的状态到结束
    :param log_id:
    :param execute_result:
    :return:
    """
    if execute_result is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = None
    if not isinstance(execute_result, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(execute_result, dict):
            # 如果是dict类型的,直接发
            request = execute_result
    else:
        # 说明是munch的,那么就转成Dict的
        request = execute_result.toDict()

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/sjtl-service/{log_id}/finished?triggerProcess={triggerProcess}",
                          json=request,auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return Munch(r.json())
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return update_task_status_to_finished(log_id, execute_result,triggerProcess)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e

def count_failed_task_log_by_retry_log_id(retry_log_id):
    """
    根据retryLogId查询失败的任务数量
    :param retry_log_id:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/sjtl-service/retry/{retry_log_id}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return 0
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return count_failed_task_log_by_retry_log_id(retry_log_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def count_success_task_log_by_job(job_id, update_time):
    """
    统计执行成功的任务的数量
    :param job_id:
    :param update_time: 更新时间, 格式: yyyy-MM-dd HH:mm:ss 的字符串 或者 datetime 类型
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = None
    if isinstance(update_time, str):
        request = update_time
    elif isinstance(update_time, datetime):
        request = datetime.strftime("%Y-%m-%d %H:%M:%S")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/sjtl-service/{job_id}", params={'updateTime': request},auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return 0
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return count_success_task_log_by_job(job_id, update_time)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def doing_tasks(project_code):
    """
    查询正在执行的任务
    :param project_code:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/sjtl-service/{project_code}/doing",auth=ClientAuth())
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
        return doing_tasks(project_code)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
