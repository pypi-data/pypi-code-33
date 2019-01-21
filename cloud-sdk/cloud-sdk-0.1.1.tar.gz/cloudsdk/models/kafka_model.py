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


class KafkaModel(ApiModel):
    @classmethod
    def get_kafka_info_by_user_id(cls, user_id, zone=None):
        """
        获取指定用户的所有Kafka集群
        :param user_id: 用户id
        :param zone: 区域
        :return: 返回Kafka集群信息
        """
        kafka_data = ApiModel.get_all(action='DescribeQueues', set='queue_set', zone=zone,
                                params={'owner': user_id, 'status.1': 'active', 'verbose': '1'})
        return kafka_data


    @classmethod
    def get_kafka(cls, zone=None):
        """
        获取指定区域所有Kafka集群
        :param zone: 区域
        :return: Kafka集群信息
        """
        kafka_data = ApiModel.get_all(action='DescribeQueues', set='queue_set', zone=zone,
                                params={ 'status.1': 'active', 'verbose': '1'})
        return kafka_data

if __name__ == '__main__':
    import demjson
    kafka = KafkaModel()
    print(demjson.encode(kafka.get_kafka_info_by_user_id(user_id = 'usr-jH1olhiH' ,zone='SHA')))