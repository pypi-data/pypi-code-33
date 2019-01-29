# -*- coding: utf-8 -*-

import requests
import json

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from tpspy.base import ClientBase
from tpspy.base import ResponseCode


class ClientPermission(ClientBase):

    def __init__(self, sys_id=None, sys_secret=None, tps_base_url=None):
        super(ClientPermission, self).__init__(sys_id=sys_id, sys_secret=sys_secret, tps_base_url=tps_base_url)

    def get_user_managed_group(self, token=None):
        """
        获得用户所管理的所有用户组
        :param token string
        :return: [{
                "group_id": int,
                "group_name": string
            }]
            返回一个上述结构
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/')
        try:
            resp = requests.get(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if data and code == ResponseCode.CODE_SUCCESS:
                return True, data['group_list']
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def get_user_group_detail(self, group_id, token=None):
        """
        获得用户组详情
        :param group_id: 用户组ID int
        :param token: string
        :return: owners: [{
                    "user_id": "OA::toringzhang",
                    "nick_name": "toringzhang"
                }]
                members: [{
                    "user_id": "OA::toringzhang",
                    "nick_name": "toringzhang"
                }]
                accesses: [{
                        "target_id": "athena::demo",
                        "access_level": 5
                }]
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/%d/' % group_id)
        try:
            resp = requests.get(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if data and code == ResponseCode.CODE_SUCCESS:
                return True, data['owners'], data['members'], data['accesses']
            else:
                return False, resp_dict.get('msg', 'unknown error.'), None, None
        except Exception as e:
            return False, str(e), None, None

    def create_user_group(self, group_name, members=None, owners=None, token=None):
        """
        新建一个用户组
        :param group_name: 用户组名称
        :param members: 用户组成员[name]
        :param owners:  用户组管理员[name]
        :param token: string
        :return: group_name string, group_id int
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/')
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                group_name=group_name,
                members=members,
                owners=owners
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if data and code == ResponseCode.CODE_SUCCESS:
                return True, data['group_name'], data['group_id']
            else:
                return False, resp_dict.get('msg', 'unknown error.'), None
        except Exception as e:
            return False, str(e), None

    def delete_user_group(self, group_id, token=None):
        """
        删除用户组
        :param group_id: 用户组id int
        :param token:
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/%d/' % group_id)
        try:
            resp = requests.delete(url=url,  headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def add_group_member(self, group_id, members, token=None):
        """
        添加用户组成员
        :param group_id: int
        :param members: [string]
        :param token:
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/%d/add_member/' % group_id)
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                members=members,
                user_type=0,
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def add_group_owner(self, group_id, owners, token=None):
        """
        添加用户组管理员
        :param group_id: int
        :param owners: [string]
        :param token:
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/%d/add_member/' % group_id)
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                members=owners,
                user_type=1,
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def delete_group_member(self, group_id, members, token=None):
        """
        删除用户组成员
        :param group_id: int
        :param members: list
        :param token:
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/%d/delete_member/' % group_id)
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                members=members,
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def delete_group_owner(self, group_id, owners, token=None):
        """
        删除用户组管理员
        :param group_id: int
        :param owners: list
        :param token:
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/group/%d/delete_owner/' % group_id)
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                owners=owners,
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def get_user_managed_target(self, token=None):
        """
        获得用户所管理的资源
        :param token string
        :return: targets [{
                "target_id": 资源id string,
                "remark": 备注 json
            }]
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/target/')
        try:
            resp = requests.get(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if data and code == ResponseCode.CODE_SUCCESS:
                return True, data['targets']
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def create_target(self, sys_id, target_name, owners, remark=None, token=None):
        """
        创建一个资源
        :param sys_id: 平台id string
        :param target_name: 资源名称 string
        :param owners: [name]
        :param remark: {} 自定义json字段
        :param token string
        :return: 返回code=10000为成功，否则失败
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/target/')
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                sys_id=sys_id,
                target_name=target_name,
                owners=owners,
                remark=remark
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def get_target_all_access(self, target_id, token=None):
        """
        获得一个资源所有可访问的用户和用户组
        :param target_id 资源ID string
        :param token string
        :return: users: [{
                "user_id": 用户id string,
                "access_level": 权限级别 int
        }]
                groups: [{
                "group_id": 用户组id int,
                "access_level": 权限等级 int
        }]
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/target/%s/' % target_id)
        try:
            resp = requests.get(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if data and code == ResponseCode.CODE_SUCCESS:
                return True, data['users'],  data['groups']
            else:
                return False, resp_dict.get('msg', 'unknown error.'), None
        except Exception as e:
            return False, str(e), None

    def get_user_all_access_target(self, user_id, token=None):
        """
        获得用户所有有权限的产品
        :param user_id: 用户id string
        :param token: string
        :return: 产品权限列表 [{
            "target_id": string,
            "access_level": int
        }]
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/access/%s/' % user_id)
        try:
            resp = requests.get(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, data
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def get_user_to_target_access(self, user_id, target_id, token=None):
        """
        获得用户对某资源的权限
        :param user_id: string
        :param target_id: string
        :param token: string
        :return: level: int
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/access/%s/get_access/?target_id=%s' % (user_id, target_id))
        try:
            resp = requests.get(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            data = resp_dict.get('data', None)
            code = resp_dict.get('code', None)
            if data and code == ResponseCode.CODE_SUCCESS:
                return True, data['access_level']
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def create_user_to_target_access(self, target_id, user_id, access_level, token=None):
        """
        创建用户到产品的权限
        :param target_id: string
        :param user_id: string
        :param access_level: int 1~16
        :param token: string
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/access/create_user_to_target_access/')
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                target_id=target_id,
                user_id=user_id,
                access_level=access_level
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def create_group_to_target_access(self, target_id, group_id, access_level, token=None):
        """
        创建用户组到产品的权限
        :param target_id: string
        :param group_id: int
        :param access_level: int
        :param token: string
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/access/create_group_to_target_access/')
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                target_id=target_id,
                group_id=group_id,
                access_level=access_level
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def add_target_owners(self, target_id, owners, token=None):
        """
        增加资源管理员
        :param target_id: string
        :param owners: [name]
        :param token: string
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/target/%s/add_target_owners/' % target_id)
        try:
            resp = requests.post(url=url, data=json.dumps(dict(
                owners=owners
            )), headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token,
                "Content-Type": "application/json"
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)

    def delete_target(self, target_id, token=None):
        """
        删除资源
        :param target_id: 资源id，string
        :param token:
        :return:
        """
        url = urljoin(self.tps_base_url, '/api/v1/permission/target/%s/' % target_id)
        try:
            resp = requests.delete(url=url, headers={
                "SYS-ID": self.sys_id,
                "TOKEN": token or self.token
            })
            print(resp.text)
            resp_dict = json.loads(resp.text)
            code = resp_dict.get('code', None)
            if code == ResponseCode.CODE_SUCCESS:
                return True, None
            else:
                return False, resp_dict.get('msg', 'unknown error.')
        except Exception as e:
            return False, str(e)
