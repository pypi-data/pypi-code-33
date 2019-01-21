# coding=utf8
"""
-------------------------------------------------
   File Name：     eip_model
   Description :
   Author :       潘晓华
   date：          2017/9/21
-------------------------------------------------
"""
from cloudsdk.models import ApiModel


class EipModel(ApiModel):
    @classmethod
    def get_eip_info_by_eip_id(cls, eip_id, zone=None):
        eip_data = ApiModel.get_all(action='DescribeEips', set='eip_set', params={'eips.1': eip_id}, zone=zone)
        if not eip_data:
            return None
        eip_data = eip_data[0]
        return eip_data

    @classmethod
    def get_all_eip(self, zone=None):
        data_temp = self.get_all(action='DescribeEips', zone=zone, set='eip_set',
                                 params={'status.1': 'pending', 'status.2': 'available', 'status.3': 'associated',
                                         'status.4': 'suspended'})
        data = [(item['eip_addr'], item['owner'], item['billing_mode'], item['bandwidth'], item['status']) for item in data_temp]
        result = [item for item in data if item[0][0:3] != '10.' and item[0][0:3] != '99.']
        return result

    @classmethod
    def get_eip_info_by_ip(self, ip, zone=None):
        eip_data = ApiModel.get_all(action='DescribeEips', set='eip_set', params={'search_word': ip}, zone=zone)
        if not eip_data:
            return None
        eip_data2 = None
        for item in eip_data:
            if item['eip_addr'] == ip:
                eip_data2 = item
                break
        if eip_data2 == None:
            return None
        else:
            eip_data = eip_data2
        return eip_data

    @classmethod
    def get_eip_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有带宽信息
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回带宽信息
        """
        eip_data = ApiModel.get_resource_by_user_id('Eips', 'eip_set', user_id, zone)
        return eip_data

    @classmethod
    def get_eips(cls, zone=None):
        """
        获取指定区域所有带宽信息
        :param zone: 区域
        :return: 带宽信息
        """
        eip_data = ApiModel.get_resources('Eips', 'eip_set', zone)
        return eip_data
