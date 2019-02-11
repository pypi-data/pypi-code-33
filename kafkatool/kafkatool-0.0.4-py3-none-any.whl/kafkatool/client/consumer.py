#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 11:21 AM 
# @Author : xbzheng

from functools import partial
from structlog import get_logger
from kafkatool.client.sede import str_der
from kafkatool.exception import (
    ProduceWithEmptyTopic, KafkaTransportError, EndOfPartition
)
from kafkatool.metrics import (
    CONSUMER_RECEIVE_NUM, CONSUMER_ERROR_NUM
)
from kafkatool.metrics.counter import Counter, NothingCounter
from kafkatool.config.kconf import KConsumerConf
from kafkatool.client.utils import retry_exception
from kafkatool.client.callbacks import (
    default_error_cb, default_on_commit_cb, default_stats_cb,
    default_throttle_cb
)
from confluent_kafka import Consumer as CConsumer
from confluent_kafka import KafkaException
from confluent_kafka import TopicPartition


@retry_exception(exceptions=[KafkaTransportError])
def default_get_message(consumer, error_handler, timeout=1.0, stop_on_eof=False,
                        metrics=NothingCounter()):
    message = consumer.poll(timeout=timeout)
    if message is None:
        return None

    if message.error():
        metrics.incr(CONSUMER_ERROR_NUM)
        try:
            error_handler(message.error())
        except EndOfPartition:
            if stop_on_eof:
                raise
            else:
                return None
        return None

    return message


class Consumer:
    """
    kafka consumer helper class with:
        - data deserialization
        - statistic metric embedded
    """

    def __init__(self,
                 config: KConsumerConf = None,
                 value_der=str_der,
                 get_message=default_get_message,
                 msg_error_handler=default_error_cb,
                 on_commit=default_on_commit_cb,
                 error_cb=default_error_cb,
                 throttle_cb=default_throttle_cb,
                 stats_cb=None,
                 metrics=None):
        """
        Init kafka consumer client
        :param config: kafka client conf, must include 'topics'
        :param value_ser: serializer for data before send
        :param get_message: fetch message from kafka
        :param on_commit: callback when data finish commit
        :param error_cb: error callback
        :param throttle_cb: throttle callback
        :param stats_cb: stats callback
        :param metrics: a statistic instance with incr/decr/reset method, default Counter()
        """
        self.log = get_logger("Consumer")
        if not config:
            config = KConsumerConf()
        self._config = config
        # register callback to config
        self._config.attach_on_commit_cb(on_commit)
        self._config.attach_error_cb(error_cb)
        self._config.attach_stats_cb(stats_cb)
        self._config.attach_throttle_cb(throttle_cb)

        self.log.info('init consumer config', **self._config)

        self._value_der = value_der
        if not metrics:
            metrics = Counter()
        self._metrics = metrics

        self._topics = self._get_topics(self._config)
        self._stop_on_eof = self._config.pop('stop_on_eof', False)
        self._poll_timeout = self._config.pop('poll_timeout', 0.1)
        self._non_blocking = config.pop('non_blocking', False)

        self._client = CConsumer(self._config)
        self._client.subscribe(self._topics)
        self._generator = self._message_generator()

        self._get_message = partial(
            get_message, consumer=self._client, error_handler=msg_error_handler,
            timeout=self._poll_timeout, stop_on_eof=self._stop_on_eof)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._generator)
        except EndOfPartition:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # the only reason a consumer exits is when an
        # exception is raised.
        #
        # close down the consumer cleanly accordingly:
        #  - stops consuming
        #  - commit offsets (only on auto commit)
        #  - leave consumer group
        self.log.info("Closing consumer")
        self._metrics.close()
        self._client.close()

    def _message_generator(self):
        """
        :return: decode_value, raw_message
        """
        while True:
            message = self._get_message()
            if message is None:
                if self._non_blocking:
                    yield None
                continue
            decode_value = self._value_der(message.value())
            self._metrics.incr(CONSUMER_RECEIVE_NUM)
            yield decode_value, message

    def commit(self, **kwargs):
        """
        see: https://docs.confluent.io/current/clients/confluent-kafka-python/#consumer
        commit([message=None][, offsets=None][, asynchronous=True])
        :param kwargs:
        :return:
        """
        self._client.commit(**kwargs)

    @staticmethod
    def _get_topics(config):
        topics = config.pop('topics', None)
        assert topics is not None, "You must subscribe to at least one topic"

        if not isinstance(topics, list):
            topics = [topics]

        return topics

