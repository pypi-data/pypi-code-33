#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 2:52 PM 
# @Author : xbzheng

"""
Test producer
"""

import unittest

from kafkatool.config.kconf import (
    KConf, KProducerConf
)
from kafkatool.client.producer import Producer
from .config import producer_config


class TestProducer(unittest.TestCase):

    def test_single_produce(self):
        p = Producer(producer_config)
        p.produce('test', 'a')
        # p.poll()


if __name__ == '__main__':
    unittest.main()
