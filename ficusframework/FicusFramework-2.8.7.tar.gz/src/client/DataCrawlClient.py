"""
Crawl的操作模块
"""
import requests
from munch import Munch

from client import ClientAuth
from client.FicusServerGetter import ficusServerGetter
from api.exceptions import ServiceNoInstanceException, ServiceInnerException, AuthException


def get(site, project_code, code):
    """
    获取CE
    :param site: 站点
    :param project_code: 项目名
    :param code: CE的唯一code
    :return: 如果这个ce存在,返回ce对象.否则返回空
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/dc-service/{site}/{project_code}/{code}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return Munch(r.json())
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return get(site, project_code, code)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e

def exists(site, project_code, code):
    """
    校验CE是否存在
    :param site: 站点
    :param project_code: 项目名
    :param code: CE的唯一code
    :return: 如果这个ce存在,返回true.否则,返回false
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/dc-service/exists/{site}/{project_code}/{code}",auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return r.json()
        else:
            return False
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return exists(site, project_code, code)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def query(site, project_code=None, code=None, crawl_type=None, page=1, size=20):
    """
    查询Crawl
    :param site: 站点
    :param project_code: 项目名
    :param code: CE的唯一code
    :param crawl_type: crawl的类型, JDBC/FILE/WEB/CUSTOM
    :param page: 分页页码,从1开始
    :param size: 分页大小,默认20
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.get(f"{ficusServerGetter.server_url}remote/dc-service/{site}",
                         params={'projectcode': project_code, 'code': code, 'type': crawl_type, 'page': page,
                                 'size': size},auth=ClientAuth())
        r.raise_for_status()
        if len(r.content) > 0:
            return Munch(r.json())
        else:
            return None
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return query(site, project_code, code, crawl_type, page, size)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def add_crawl(data_crawl):
    """
    新增一个Crawl
    :param data_crawl: crawl对象
    :return: 如果添加失败,就抛出异常,否则无返回
    """
    if data_crawl is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    request = None
    if not isinstance(data_crawl, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(data_crawl, dict):
            # 如果是dict类型的,直接发
            request = data_crawl
    else:
        # 说明是munch的,那么就转成Dict的
        request = data_crawl.toDict()

    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/dc-service/", json=request,auth=ClientAuth())
        r.raise_for_status()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        add_crawl(data_crawl)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
