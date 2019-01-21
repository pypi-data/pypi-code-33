# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     snapshots_model
   Description :
   Author :       潘晓华
   date：          2018/2/28
-------------------------------------------------
"""


from cloudsdk.models import ApiModel

class SnapshotsModel(ApiModel):
    @classmethod
    def get_snapshot_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有备份信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回备份信息
        """
        snapshots_data = ApiModel.get_resource_by_user_id('Snapshots', 'snapshot_set', user_id, zone)
        return snapshots_data


    @classmethod
    def get_snapshots(cls, zone=None):
        """
        获取指定区域所有备份信息
        :param zone: 区域
        :return: 备份信息
        """
        snapshots_data = ApiModel.get_resources('Snapshots', 'snapshot_set', zone)
        return snapshots_data
