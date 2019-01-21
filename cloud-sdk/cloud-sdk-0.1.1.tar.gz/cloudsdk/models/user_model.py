# coding=utf8
"""
-------------------------------------------------
   File Name：     user_model
   Description :
   Author :       潘晓华
   date：          2017/9/21
-------------------------------------------------
"""

from cloudsdk.models import ApiModel


class UserModel(ApiModel):
    @classmethod
    def get_user_info_by_user_id(cls, user_id):
        user_data = ApiModel.get_all(action='DescribeUsers', set='user_set', params={'users.1': user_id})
        if not user_data:
            return None
        user_data = user_data[0]
        return user_data

    @classmethod
    def get_all_user(cls, zone=None):
        """
        获取所有用户信息
        :return:用户信息
        """
        data_temp = cls.get_all(action='DescribeUsers', set='user_set', params={"status.1": "active"}, zone=zone)
        return data_temp

    @classmethod
    def update_user_info_by_user_id(cls, user_id, params):
        request_params = {
            'user': user_id
        }
        if not None == params:
            request_params = dict(request_params, **params)
        return cls.request(action='ModifyUserAttributes', params=request_params)