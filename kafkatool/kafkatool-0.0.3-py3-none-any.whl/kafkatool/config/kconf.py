#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 2:21 PM 
# @Author : xbzheng

import socket
import os
import yaml

DEFAULT_PRODUCER_CONFIG = {
    'acks': 'all',
    'api.version.request': True,
    'client.id': socket.gethostname(),
    'log.connection.close': False,
    'max.in.flight': 1,
    'queue.buffering.max.ms': 100,
    'statistics.interval.ms': 15000,
}

DEFAULT_CONSUMER_CONFIG = {
    'api.version.request': True,
    'client.id': socket.gethostname(),
    # 'default.topic.config': {
    #     'auto.offset.reset': 'latest'
    # },
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    # 'fetch.error.backoff.ms': 500,
    # 'fetch.wait.max.ms': 100,
    'fetch.min.bytes': 1,
    'log.connection.close': False,
    'log.thread.name': False,
    'session.timeout.ms': 10000,
    'statistics.interval.ms': 0,
    'offset.store.method': 'broker'
}


class KConf(dict):
    """
    confluent kafka config helper
    detail: https://docs.confluent.io/current/clients/confluent-kafka-python/#configuration
    """

    def __init__(self, conf_dict=None, *conf_files, **kwargs):
        """
        import kafka config from user defined dict or other resource
        detail conf see: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
        :param conf_dict: user defined dict
        :param conf_files: outside conf files
        :param kwargs: kv pair conf
        """
        super().__init__(**kwargs)
        self.update(KConf.load_conf_file(conf_files))
        if conf_dict is None:
            conf_dict = {}
        self.update(conf_dict)

    @staticmethod
    def load_conf_file(files):
        conf_dict = {}

        for file in files:
            (file_path, filename) = os.path.split(file)
            (short_name, extension) = os.path.splitext(filename)
            if extension == '.yaml':
                conf_dict.update(KConf._load_yaml_conf_file(file))
            else:
                raise NotImplementedError('conf file only support yaml now')
        return conf_dict

    @staticmethod
    def _load_yaml_conf_file(file):
        with open(file) as config_file:
            return yaml.load(config_file)

    def attach_error_cb(self, cb):
        if cb:
            self['error_cb'] = cb

    def attach_stats_cb(self, cb):
        if cb:
            self['stats_cb'] = cb

    def attach_throttle_cb(self, cb):
        if cb:
            self['throttle_cb'] = cb


class KConsumerConf(KConf):
    """
    kafka conf class with default consumer conf
    """

    def __init__(self, conf_dict=None, *conf_files, **kwargs):
        super().__init__({**DEFAULT_CONSUMER_CONFIG, **conf_dict}, *conf_files, **kwargs)

    def attach_on_commit_cb(self, cb):
        if cb:
            self['on_commit'] = cb


class KProducerConf(KConf):
    """
    kafka conf class with default producer conf
    """

    def __init__(self, conf_dict=None, *conf_files, **kwargs):
        super().__init__({**DEFAULT_PRODUCER_CONFIG, **conf_dict}, *conf_files, **kwargs)

    def attach_on_delivery_cb(self, cb):
        if cb:
            self['on_delivery'] = cb


