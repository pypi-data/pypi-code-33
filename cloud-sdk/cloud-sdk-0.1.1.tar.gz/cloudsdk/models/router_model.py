# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     router_model
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

class RouterModel(ApiModel):
    @classmethod
    def get_router_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有路由器信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回路由器信息
        """
        router_data = ApiModel.get_resource_by_user_id('Routers', 'router_set', user_id, zone)
        return router_data


    @classmethod
    def get_routers(cls, zone=None):
        """
        获取指定区域所有路由器信息
        :param zone: 区域
        :return: 路由器信息
        """
        routers_data = ApiModel.get_resources('Routers', 'router_set', zone)
        return routers_data

    @classmethod
    def get_router_info_by_router_id(cls, router_id, zone=None):
        """
        获取指定区域指定router_id的路由器信息
        :param router_id: vpc的id
        :param zone: 区域
        :return: 路由器信息
        """

        routers_data = ApiModel.get_all(action='DescribeRouters', set='router_set',
                                        params={'routers.1': router_id, "verbose": 1}, zone=zone)
        return routers_data

if __name__ == '__main__':
    pass
