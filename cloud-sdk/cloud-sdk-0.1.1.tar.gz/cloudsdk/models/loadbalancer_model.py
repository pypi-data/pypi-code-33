# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     loadbalancer_model
   Description :
   Author :       潘晓华
   date：          2018/1/29
-------------------------------------------------
"""

from cloudsdk.models import ApiModel

class LoadbalancerModel(ApiModel):
    @classmethod
    def get_loadbalance_info_by_id(cls, loadbalancer_id, zone=None):
        loadbalancer_data = ApiModel.get_all(action='DescribeLoadBalancers', set='loadbalancer_set', zone=zone,
                                         params={'loadbalancers.1': loadbalancer_id})
        if not loadbalancer_data:
            return None
        loadbalancer_data = loadbalancer_data[0]
        return loadbalancer_data

    @classmethod
    def get_loadbalancer_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有负载均衡信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回负载均衡信息
        """
        loadbalancer_data = ApiModel.get_resource_by_user_id('LoadBalancers', 'loadbalancer_set', user_id, zone)
        return loadbalancer_data

    @classmethod
    def get_loadbalancers(cls, zone=None):
        """
        获取指定区域所有负载均衡信息
        :param zone: 区域
        :return: 负载均衡信息
        """
        loadbalancer_data = ApiModel.get_resources('LoadBalancers', 'loadbalancer_set', zone)
        return loadbalancer_data
