# coding=utf8
"""
-------------------------------------------------
   File Name：     bots_model
   Description :
   Author :        秦玉微
   date：          2018/1/4
-------------------------------------------------
"""
from cloudsdk.models import ApiModel
from cloudsdk.api.api_cloud import ApiCloud
from cloudsdk.config import ApiConfig


class BotsModel(ApiModel):
    @classmethod
    def get_describebots(cls, zone=None, cache=True):
        """
        获取符合条件的物理资源信息
        :param zone:
        :return:物理资源信息
        """
        params = {}
        params['status.1'] = 'faulty'  # 故障
        params['status.2'] = 'rescuing'  # 修复中
        params['status.3'] = 'active'  # 可用
        params['status.4'] = 'standby'  # 待命中
        bots_data = ApiModel.get_all(action='DescribeBots', set='bot_set', zone=zone, params=params)
        return bots_data

    @classmethod
    def get_bot_monitor_by_id(cls, node_id, meter, items, zone=None):
        """
        获取物理主机的资源使用情况信息
        :param zone: 区域
        :return: 
        """
        if None == zone:
            zone = ApiConfig.api_default_zone
        bot_monitor_info = ApiCloud.request(
            action_data={"action": "GetBOSSMonitor", "scope": "zone.%s" % zone, "monitor": "daemon",
                         "resource_type": "physical", 'resource': node_id,
                         "topics.0.meter": meter, "topics.0.items": items,
                         "interval": "12h"})
        data = bot_monitor_info['monitor_set'][0]['data']
        return data.keys(), data
        # import time, datetime
        # for (item, value) in data:
        #     timeArray = time.localtime(int(item))
        #     otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
        #     print otherStyleTime, value

    @classmethod
    def get_describebot_by_id(cls, node_id, zone=None):
        params = {'bots.0': node_id}
        bots_data = ApiModel.get_all(action='DescribeBots', set='bot_set', zone=zone, params=params)
        return bots_data
