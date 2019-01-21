# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     rdb_model
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

class RdbModel(ApiModel):
    @classmethod
    def get_rdb_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有关系型数据库信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回关系型数据库信息
        """
        rdb_data = ApiModel.get_all(action='DescribeRDBs', set='rdb_set', zone=zone,
                                params={'owner': user_id, 'status.1': 'active', 'verbose': '1'})
        return rdb_data


    @classmethod
    def get_rdbs(cls, zone=None):
        """
        获取指定区域所有关系型数据库信息
        :param zone: 区域
        :return: 关系型数据库信息
        """
        rdbs_data = ApiModel.get_all(action='DescribeRDBs', set='rdb_set', zone=zone,
                                params={ 'status.1': 'active', 'verbose': '1'})
        return rdbs_data

if __name__ == '__main__':
    pass
