# coding=utf8
"""
-------------------------------------------------
   File Name：     zone_model
   Description :
   Author :       潘晓华
   date：          2017/9/22
-------------------------------------------------
"""

from cloudsdk.models import ApiModel

class ZoneModel(ApiModel):
    @classmethod
    def get_all_zone(cls):
        zones = ApiModel.get_all(action='DescribeZones', set='zone_set', params={'status': 'active'})
        zone_ids = [item['zone_id'] for item in zones]
        if not zone_ids:
            return None
        return zone_ids

