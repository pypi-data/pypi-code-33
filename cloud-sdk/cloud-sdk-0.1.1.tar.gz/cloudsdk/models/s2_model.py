# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     s2_model
   Description :
   Author :       潘晓华
   date：          2018/1/29
-------------------------------------------------
"""

from cloudsdk.models import ApiModel

class S2Model(ApiModel):
    @classmethod
    def get_s2_info_by_id(cls, s2_id, zone=None):
        s2_data = ApiModel.get_all(action='DescribeS2Servers', set='s2_server_set', zone=zone,
                                         params={'s2_servers.1': s2_id})
        if not s2_data:
            return None
        s2_data = s2_data[0]
        return s2_data

    @classmethod
    def get_s2_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有共享存储信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回共享存储信息
        """
        s2_data = ApiModel.get_all(action='DescribeS2Servers', set='s2_server_set', zone=zone,
                                    params={'owner': user_id, 'status.1': 'active', 'verbose': '1'})
        return s2_data

    @classmethod
    def get_s2s(cls, zone=None):
        """
        获取指定区域所有关系型数据库信息
        :param zone: 区域
        :return: 关系型数据库信息
        """
        s2_data = ApiModel.get_all(action='DescribeS2Servers', set='s2_server_set', zone=zone,
                                     params={'status.1': 'active', 'verbose': '1'})
        return s2_data
