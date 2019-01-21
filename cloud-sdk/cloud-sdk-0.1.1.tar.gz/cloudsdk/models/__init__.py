# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     __init__.py
   Description :
   Author :       潘晓华
   date：          2019/1/15
-------------------------------------------------
"""


# coding=utf8
"""
-------------------------------------------------
   File Name：     api_model
   Description :
   Author :       潘晓华
   date：          2017/8/21
-------------------------------------------------
"""
from cloudsdk.api.api_cloud import ApiCloud
import math
from cloudsdk.config import ApiConfig


class ApiModel(object):
    limit = 99

    @classmethod
    def get_all_by_page(cls, action='', set='', zone=None, params=None, page=0, per_page=99):
        if None == zone:
            zone = ApiConfig.api_default_zone
        action_data = {
            'action': action,
            'limit': per_page,
            'zone': zone,
            'offset': page * per_page
        }
        if not None == params:
            action_data = dict(action_data, **params)

        result = ApiCloud.request(action_data=action_data)
        if 'total_count' not in result:
            return [], 0

        total_count = result['total_count']
        data = result[set]

        return data, total_count

    @classmethod
    def get_all(cls, action='', set='', zone=None, params=None):
        if None == zone:
            zone = ApiConfig.api_default_zone
        action_data = {
            'action': action,
            'limit': cls.limit,
            'zone': zone
        }
        if not None == params:
            action_data = dict(action_data, **params)
        first_result = ApiCloud.request(action_data=action_data)
        if 'total_count' not in first_result:
            if set not in first_result:
                return list()
            else:
                return first_result[set]
        total_count = first_result['total_count']
        data = first_result[set]
        if total_count <= cls.limit:
            return data
        pages = math.ceil(total_count / float(cls.limit))
        for i in range(1, int(pages)):
            action_data['offset'] = i * cls.limit
            temp_result = ApiCloud.request(action_data=action_data)
            data += temp_result[set]
        return data

    @classmethod
    def get_resource_by_user_id(cls, resource=None, set=None, user_id=None, zone=None):
        if None == resource or None == set or None == user_id:
            return None
        data = ApiModel.get_all(action='Describe' + resource, set=set, zone=zone,
                                params={'owner': user_id, 'status.1': 'available', 'status.2': 'associated',
                                        'status.3': 'running', 'status.4': 'in-use', 'status.5': 'active',
                                        "verbose": "1"})
        return data

    @classmethod
    def get_resources(cls, resource=None, set=None, zone=None):
        if None == resource or None == set:
            return None
        data = ApiModel.get_all(action='Describe' + resource, set=set, zone=zone,
                                params={'status.1': 'available', 'status.2': 'associated',
                                        'status.3': 'running', 'status.4': 'in-use', 'status.5': 'active',
                                        "verbose": "1"})
        return data

    @classmethod
    def request(cls, action='', zone=None, params={}):
        action_data = {
            'action': action,
            'zone': zone
        }
        if not None == params:
            action_data = dict(action_data, **params)

        result = ApiCloud.request(action_data=action_data)
        return result['ret_code']
