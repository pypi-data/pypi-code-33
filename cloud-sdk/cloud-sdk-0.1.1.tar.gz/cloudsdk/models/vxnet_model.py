# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     vxnet_model
   Description :
   Author :       潘晓华
   date：          2018/3/2
-------------------------------------------------
"""


from cloudsdk.models import ApiModel

class VxnetModel(ApiModel):
    @classmethod
    def get_vxnet_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有私网信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回路由器信息
        """
        vxnet_data = ApiModel.get_resource_by_user_id('Vxnets', 'vxnet_set', user_id, zone)
        return vxnet_data


    @classmethod
    def get_vxnets(cls, zone=None):
        """
        获取指定区域所有私网信息
        :param zone: 区域
        :return: 路由器信息
        """
        vxnet_data = ApiModel.get_resources('Vxnets', 'vxnet_set', zone)
        return vxnet_data

    @classmethod
    def get_vxnet_info_by_vxnet_id(cls, vxnet_id, zone=None):
        """
        获取指定区域指定vxnet_id的私网信息
        :param router_id: vpc的id
        :param zone: 区域
        :return: 路由器信息
        """

        vxnet_data = ApiModel.get_all(action='DescribeVxnets', set='vxnet_set',
                                        params={'vxnets.1': vxnet_id}, zone=zone)
        return vxnet_data

if __name__ == '__main__':
    pass
