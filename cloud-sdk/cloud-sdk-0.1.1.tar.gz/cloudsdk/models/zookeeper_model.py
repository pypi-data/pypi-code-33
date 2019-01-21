# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hadoop_model
   Description :
   Author :       潘晓华
   date：          2018/10/29
-------------------------------------------------
"""


from cloudsdk.models import ApiModel


class ZookeeperModel(ApiModel):
    @classmethod
    def get_zookeeper_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有Hadoop集群
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回Hadoop集群信息
        """
        zookeeper_data = ApiModel.get_all(action='DescribeZookeepers', set='zookeeper_set', zone=zone,
                                params={'owner': user_id, 'status.1': 'active', 'verbose': '1'})
        return zookeeper_data


    @classmethod
    def get_zookeeper(cls, zone=None):
        """
        获取指定区域所有Hadoop集群
        :param zone: 区域
        :return: Hadoop集群信息
        """
        zookeeper_data = ApiModel.get_all(action='DescribeZookeepers', set='zookeeper_set', zone=zone,
                                params={ 'status.1': 'active', 'verbose': '1'})
        return zookeeper_data

if __name__ == '__main__':
    import demjson
    zookeeper = ZookeeperModel()
    print(demjson.encode(zookeeper.get_zookeeper_info_by_user_id(user_id = 'usr-jH1olhiH' ,zone='SHA')))