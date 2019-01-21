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


class MongosModel(ApiModel):
    @classmethod
    def get_mongos_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有关系型数据库信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回关系型数据库信息
        """
        mongos_data = ApiModel.get_all(action='DescribeMongos', set='mongo_set', zone=zone,
                                params={'owner': user_id, 'status.1': 'active', 'verbose': '1'})
        return mongos_data


    @classmethod
    def get_mongos(cls, zone=None):
        """
        获取指定区域所有关系型数据库信息
        :param zone: 区域
        :return: 关系型数据库信息
        """
        mongos_data = ApiModel.get_all(action='DescribeMongos', set='mongo_set', zone=zone,
                                params={ 'status.1': 'active', 'verbose': '1'})
        return mongos_data

if __name__ == '__main__':
    import demjson
    mongo = MongosModel()
    print(demjson.encode(mongo.get_mongos_info_by_user_id('usr-MLWEj1ET', zone='SHA')))