#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/24 4:09 PM 
# @Author : xbzheng


from kafkatool.client.consumer import Consumer
from kafkatool.config.kconf import KConsumerConf
from kafkatool.client.sede import json_der
import time
import datetime

consumer_config = KConsumerConf({'auto.offset.reset': 'earliest'}, './consumer_conf.yaml')
start = time.time()
with Consumer(consumer_config, value_der=json_der, on_commit=None) as client:
    for msg, raw in client:
        # do work here
        # print(msg)
        # print(f"{raw.partition()},{raw.offset()},{raw.topic()}")
        client.commit(message=raw, asynchronous=True)
end = time.time()
print(f"total time: {(end-start)} seconds")
