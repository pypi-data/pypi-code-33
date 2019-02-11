#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 11:21 AM 
# @Author : xbzheng

import atexit
from structlog import get_logger
from kafkatool.client.sede import str_ser
from kafkatool.exception import ProduceWithEmptyTopic
from kafkatool.metrics import (PRODUCER_SEND_NUM, PRODUCER_ERROR_NUM, PRODUCER_BUFFER_FULL_NUM)
from kafkatool.config.kconf import KProducerConf
from kafkatool.metrics.counter import Counter
from kafkatool.client.callbacks import (
    default_error_cb, default_on_deliver_cb, default_stats_cb,
    default_throttle_cb
)
from confluent_kafka import Producer as CProducer
from confluent_kafka import KafkaException


class Producer:
    """
    kafka producer helper class with:
        - data serialization
        - statistic metric embedded
    """

    def __init__(self,
                 config=None,
                 value_ser=str_ser,
                 poll_timeout=0,
                 on_delivery=default_on_deliver_cb,
                 error_cb=default_error_cb,
                 throttle_cb=default_throttle_cb,
                 stats_cb=None,
                 metrics=None):
        """
        Init kafka producer client
        :param config: kafka client conf
        :param value_ser: serializer for data before send
        :param on_delivery: callback when data finish delivery
        :param error_cb: error callback
        :param throttle_cb: throttle callback
        :param stats_cb: stats callback
        :param metrics: a statistic instance with incr/decr/reset method, default Counter()
        """
        self.log = get_logger("Producer")

        if not config:
            config = KProducerConf()
        self._config = config
        # register callback to config
        self._config.attach_on_delivery_cb(on_delivery)
        self._config.attach_error_cb(error_cb)
        self._config.attach_stats_cb(stats_cb)
        self._config.attach_throttle_cb(throttle_cb)

        self.log.info('init producer config', **self._config)

        self._value_ser = value_ser
        self._poll_timeout = poll_timeout
        if not metrics:
            metrics = Counter()
        self._metrics = metrics

        self._client = CProducer(self._config)
        atexit.register(self.close)

    def produce(self, topic, value, key=None, **kwargs):
        """
        produce it!
        :param topic: topic
        :param value: value to produce which will be serialized by self.value_ser
        :param key: message key
        :param kwargs: free add paras describe in: https://docs.confluent.io/current/clients/confluent-kafka-python/#producer
        """
        if not topic:
            raise ProduceWithEmptyTopic('Empty topic')

        if self._value_ser:
            value = self._value_ser(value)

        try:
            self._client.produce(topic=topic, value=value, key=key, **kwargs)
            self.poll(0)
            self._metrics.incr(PRODUCER_SEND_NUM)
        except BufferError as e:
            self.log.warning('produce queue full', msg=e, act='start flush it!')
            self._metrics.incr(PRODUCER_BUFFER_FULL_NUM)
            self.flush()
            self.log.info('produce queue full', msg='finish flush it!')
            # reproduce
            self._client.produce(topic=topic, value=value, key=key, **kwargs)
            self.poll(0)
            self._metrics.incr(PRODUCER_SEND_NUM)
        except (KafkaException, NotImplementedError) as e:
            self.log.error('produce err', msg=e)
            self._metrics.incr(PRODUCER_ERROR_NUM)

    def close(self):
        self._metrics.close()
        self.log.info("Flushing producer")
        self.flush()
        self.log.info("Finish flushing producer")

    def flush(self):
        self._client.flush()

    def poll(self, timeout=0):
        self._client.poll(timeout)


