#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 2:52 PM 
# @Author : xbzheng

"""
Test KConf
"""

import unittest
from .config import test_conf
from kafkatool.config.kconf import (
    KConf, KConsumerConf, KProducerConf, DEFAULT_PRODUCER_CONFIG, DEFAULT_CONSUMER_CONFIG
)


class TestKConf(unittest.TestCase):

    def test_kconf_init(self):
        kconf = KConf({'k1': 'v1'})
        self.assertEqual(kconf['k1'], 'v1')

    def test_kconf_init_from_file(self):
        kconf = KConf({}, test_conf)
        expect_dict = {
            'bootstrap.servers': "a:1,b:2,c:3",
            'group.id': 'test_group2',
            'auto.offset.reset': 'latest'
        }
        self.assertDictEqual(expect_dict, kconf)

    def test_kconf_consumer(self):
        kconf = KConsumerConf({'k1': 'v1'})
        self.assertDictEqual({**DEFAULT_CONSUMER_CONFIG, 'k1': 'v1'}, kconf)

    def test_kconf_producer(self):
        kconf = KProducerConf({'k1': 'v1'})
        self.assertDictEqual({**DEFAULT_PRODUCER_CONFIG, 'k1': 'v1'}, kconf)


if __name__ == '__main__':
    unittest.main()
