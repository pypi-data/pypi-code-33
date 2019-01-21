# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     volume_model
   Description :
   Author :       潘晓华
   date：          2018/2/28
-------------------------------------------------
"""

from cloudsdk.models import ApiModel


class VolumeModel(ApiModel):
    @classmethod
    def get_volume_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有存储信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回存储信息
        """
        volume_data = ApiModel.get_resource_by_user_id('Volumes', 'volume_set', user_id, zone)
        return volume_data


    @classmethod
    def get_volumes(cls, zone=None):
        """
        获取指定区域所有存储信息
        :param zone: 区域
        :return: 存储信息
        """
        volumes_data = ApiModel.get_resources('Volumes', 'volume_set', zone)
        return volumes_data

if __name__ == '__main__':
    pass
