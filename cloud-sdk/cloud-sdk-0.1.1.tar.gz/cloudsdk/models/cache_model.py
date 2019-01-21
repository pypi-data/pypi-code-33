# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     cache_model
   Description :
   Author :       潘晓华
   date：          2018/3/2
-------------------------------------------------
"""


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


class CacheModel(ApiModel):
    @classmethod
    def get_cache_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有缓存信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回缓存信息
        """
        cache_data = ApiModel.get_resource_by_user_id('Caches', 'cache_set', user_id, zone=None)
        return cache_data


    @classmethod
    def get_caches(cls, zone=None):
        """
        获取指定区域所有缓存信息
        :param zone: 区域
        :return: 缓存信息
        """
        caches_data = ApiModel.get_resources('Caches', 'cache_set', zone)
        return caches_data

if __name__ == '__main__':
    pass
