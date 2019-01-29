"""
认证模块操作
"""
import requests
from munch import Munch

from api.exceptions import ServiceNoInstanceException, IllegalArgumentException
from client import ficusServerGetter


def oauth_access_token(client_id, client_secret):
    """
    获取oauth系统认证的accessToken
    :param client_id:
    :param client_secret:
    :return:
    """
    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(
            f"{ficusServerGetter.server_url}oauth/token?grant_type=client_credentials&scope=select&client_id={client_id}&client_secret={client_secret}")
        r.raise_for_status()
        if len(r.content) > 0:
            entity = Munch(r.json())

            from datetime import datetime
            import time
            return (entity["access_token"], datetime.fromtimestamp(time.time() + entity["expires_in"]))
        else:
            return (None, None)
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return oauth_access_token(client_id, client_secret)
    except requests.exceptions.HTTPError as ee:
        raise IllegalArgumentException(f"从ficus获取oauth签名失败,{ee.response.status_code}")


def oauth_jwt_token(user_name, user_password):
    """
    获取jwt的用户内容权限的jwtToken
    :param user_name:
    :param user_password:
    :return:
    """

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    try:
        r = requests.post(f"{ficusServerGetter.server_url}user/login",
                          json={"username": user_name, "password": user_password})
        r.raise_for_status()
        if len(r.content) > 0:
            jwt_token = r.text

            return (jwt_token, _find_expiration(jwt_token))
        else:
            return (None, None)
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        return oauth_jwt_token(user_name, user_password)
    except requests.exceptions.HTTPError as ee:
        raise IllegalArgumentException(f"从ficus获取用户认证失败,{ee.response.status_code}")


def _find_expiration(jwt_token:str):
    """
    解析jwtToken的过期时间
    :param jwt_token:
    :return:
    """

    # jwt有三部分,每个部分用逗号分隔.
    if jwt_token is None:
        return None

    splits = jwt_token.split(".")

    # 取第二部分
    s = splits[1]

    # 把第二部分用base64解码.
    import base64
    s1 = base64.b64decode(s)

    # 出来是一个map,取exp字段
    import json
    json_object = json.loads(s1)

    exp = json_object["exp"]

    from datetime import datetime
    return datetime.fromtimestamp(exp)
