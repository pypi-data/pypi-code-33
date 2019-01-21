# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     quota_model
   Description :   获取某些资源类型的配额信息
   Author :       潘晓华
   date：          2018/6/11
-------------------------------------------------
"""
from datetime import timedelta


from cloudsdk.models import ApiModel

class QuotaModel(object):
    @classmethod
    def get_quota_by_uid(cls, user_id=None, zone=None):
        """
        获取当前用户的配额额度
        :param uid: 用户id
        :param zone: 可用区域
        :return: 配额额度数据
        """

        quota_data= ApiModel.get_all(action="DescribeQuotas", set="quota_set", params={"users.1": user_id}, zone=zone)
        if not quota_data:
            return quota_data

        quota_data = quota_data[0]
        quota_data_result = {item: (int(value) if type(value) == int or value.isdigit() else value) for item, value in quota_data.iteritems()}
        return quota_data_result

    @classmethod
    def get_quota_left_by_uid(cls, user_id=None, zone=None):
        """
        获取当前用户剩余的配额
        :param uid: 用户id
        :param zone: 可用区域
        :return: 用户剩余的配额数据
        """
        quota_left_data = ApiModel.get_all(action='GetQuotaLeft', set='quota_left_set', params={'user': user_id}, zone=zone)
        if not quota_left_data:
            return quota_left_data
        quota_left_data = {item['resource_type']: item['left'] for item in quota_left_data}
        quota_left_data_result = {item: int(value) if type(value) == int or value.isdigit() else value for item, value in quota_left_data.iteritems()}
        return quota_left_data_result

if __name__ == '__main__':
    pass