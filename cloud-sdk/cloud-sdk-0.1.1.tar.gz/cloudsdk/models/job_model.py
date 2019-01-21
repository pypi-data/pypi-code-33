# coding=utf8
"""
-------------------------------------------------
   File Name：     jobs_model
   Description :
   Author :       潘晓华
   date：          2017/9/21
-------------------------------------------------
"""
import datetime
import json
from cloudsdk.models import ApiModel
from cloudsdk.models.instance_model import InstanceModel
from cloudsdk.models.user_model import UserModel
from cloudsdk.models.zone_model import ZoneModel


class JobModel(ApiModel):
    @classmethod
    def get_migration_info(self, zone, start_time, end_time):
        """
        获得指定区域最近的迁移事件
        :param zone: 区域
        :param start_time: 开始时间
        :return: 迁移事件信息
        """
        migrate_data = ApiModel.get_all(action='DescribeJobs', set='job_set', zone=zone,
                                        params={'job_action.1': 'MigrateInstances', "owner": "yunify",
                                                'start_time': start_time, 'end_time': end_time})
        data = []
        for migrate_item in migrate_data:
            migrate_item['directive'] = json.loads(migrate_item['directive'])
            if not migrate_item['directive']['instances']:
                continue
            migrate_item['zone'] = zone
            create_time = datetime.datetime.strptime(migrate_item['create_time'],
                                                     '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
            migrate_item['create_time'] = create_time.strftime("%Y-%m-%d %H:%M:%S")
            instance_info = InstanceModel.get_instance_info_by_instance_id(migrate_item['directive']['instances'][0],
                                                                           zone)

            if not instance_info:
                continue
            user_info = UserModel.get_user_info_by_user_id(instance_info['owner'])
            migrate_item['instance_info'] = instance_info
            migrate_item['instance_info']['image'] = eval(instance_info['image']) if not isinstance(
                instance_info['image'],
                dict) else instance_info[
                'image']
            migrate_item['instance_info']['vxnets'] = eval(instance_info['vxnets']) if not isinstance(
                instance_info['vxnets'], list) else instance_info['vxnets']
            migrate_item['user'] = user_info
            data.append(migrate_item)
        return migrate_data

    @classmethod
    def get_migration_data_latest(cls, days=1):
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        zones = ZoneModel.get_all_zone()
        migrate_data = []
        for zone in zones:
            migrate_data = migrate_data + cls.get_migration_info(zone=zone,
                                                                 start_time=yesterday.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                                 end_time=datetime.datetime.utcnow().strftime(
                                                                     '%Y-%m-%dT%H:%M:%SZ'))
        data_by_account = {}
        for migrate_item in migrate_data:
            user_id = migrate_item['user']['user_id']
            data_by_account.setdefault(user_id, []).append(migrate_item)
        return data_by_account

    @classmethod
    def get_migration_data_by_select_time(cls, from_time, to_time):
        start_time = datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M')-datetime.timedelta(hours=8)
        end_time = datetime.datetime.strptime(to_time, '%Y-%m-%d %H:%M')-datetime.timedelta(hours=8)
        zones = ZoneModel.get_all_zone()
        migrate_data = []
        for zone in zones:
            migrate_data = migrate_data + cls.get_migration_info(zone=zone,
                                                                 start_time=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                                 end_time=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'))
        data_by_account = {}
        for migrate_item in migrate_data:
            user_id = migrate_item['user']['user_id']
            data_by_account.setdefault(user_id, []).append(migrate_item)
        return data_by_account