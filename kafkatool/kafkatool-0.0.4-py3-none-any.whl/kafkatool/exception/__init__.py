#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 11:21 AM 
# @Author : xbzheng


class ProduceWithEmptyTopic(Exception):
    """
    Raised when produce with empty topic
    """
    pass


class EndOfPartition(Exception):
    """ We have reached the end of a partition """


class KafkaTransportError(Exception):
    """
    Kafka transport errors:
        - GroupCoordinator response error: Local: Broker transport failure
    """