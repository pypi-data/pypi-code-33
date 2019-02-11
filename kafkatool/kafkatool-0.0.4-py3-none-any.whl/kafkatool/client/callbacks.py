#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2018/12/21 3:25 PM
# @Author : xbzheng

import json
from typing import List
from confluent_kafka import (KafkaError, Message, ThrottleEvent, TopicPartition)
from structlog import get_logger

log = get_logger('callbacks')


def message_detail(msg):
    data = {
        'key': msg.key(),
        'partition': msg.partition(),
        'offset': msg.offset(),
        'topic': msg.topic(),
        'value': str(msg.value())
    }
    return json.dumps(data)


def default_on_deliver_cb(err: KafkaError, msg: Message):
    if err:
        log.error("[on_deliver-fail]", err=err)
    else:
        log.info("[on_deliver-succ]", key=msg.key(), partition=msg.partition(), offset=msg.offset,
                 topic=msg.topic, value=str(msg.value))


def topic_partition_detail(p: TopicPartition):
    info = {
        "topic": p.topic,
        "partition": p.partition,
        "offset": p.offset
    }
    return json.dumps(info)


def default_on_commit_cb(err: KafkaError, partitions: List[TopicPartition]):
    if err:
        log.error("[on_commit error]", err=err)
    else:
        log.info("[on_commit]", info=[topic_partition_detail(p) for p in partitions])


def default_error_cb(err: KafkaError):
    log.error("[error]", err=err)


def default_throttle_cb(event: ThrottleEvent):
    log.warning("[throttle]", event=event)


def default_stats_cb(json_str):
    log.info("[stats]", json_str=json_str)

# def default_error_cb(kafka_error):
#     code = kafka_error.code()
#     if code == KafkaError._PARTITION_EOF:
#         raise EndOfPartition
#     elif code == KafkaError._TRANSPORT:
#         statsd.increment(f'{base_metric}.consumer.message.count.error')
#         raise KafkaTransportError(kafka_error)
#     else:
#         statsd.increment(f'{base_metric}.consumer.message.count.error')
#         raise KafkaException(kafka_error)
