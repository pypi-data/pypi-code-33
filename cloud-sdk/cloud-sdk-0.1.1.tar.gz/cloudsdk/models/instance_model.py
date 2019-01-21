# coding=utf8
"""
-------------------------------------------------
   File Name：     instance_model
   Description :
   Author :       潘晓华
   date：          2017/9/21
-------------------------------------------------
"""

from cloudsdk.models import ApiModel


class InstanceModel(ApiModel):
    @classmethod
    def get_instance_info_by_instance_id(cls, instance_id, zone=None):
        instance_data = ApiModel.get_all(action='DescribeInstances', set='instance_set', zone=zone,
                                         params={'instances.0': instance_id})
        if not instance_data:
            return None
        instance_data = instance_data[0]
        return instance_data

    @classmethod
    def get_instance_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有主机信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回主机信息
        """
        instances_data = ApiModel.get_resource_by_user_id('Instances', 'instance_set', user_id, zone)
        return instances_data

    @classmethod
    def get_instances(cls, zone=None):
        """
        指定区域所有主机信息
        :param zone: 区域
        :return: 主机信息
        """
        instances_data = ApiModel.get_resources('Instances', 'instance_set', zone)
        return instances_data

    @classmethod
    def get_instance_info_by_bot_id(cls, bot_id, zone=None):
        """
        获取指定物理主机下的虚拟机
        :param bot_id:宿主机id
        :param zone:宿主机所在的zone
        :return:物理主机数据
        """

        instances_data = ApiModel.get_all(action='DescribeInstances', set='instance_set', zone=zone,
                                          params={'host_machine': bot_id, 'status.0': 'pending', 'status.1': 'running',
                                                  'status.2': 'stopped', 'status.3': 'suspended',
                                                  'status.4': 'terminated'})
        if not instances_data:
            return None
        return instances_data
