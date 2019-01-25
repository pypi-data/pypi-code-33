#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the bundler module."""
from __future__ import absolute_import
import os
from unittest import TestCase
from pacifica.uploader.common import CommonBase


class TestCommonModule(TestCase):
    """Test the bundler module for exported classes."""

    def test_common_basic(self):
        """Test the bundler to stream a tarfile."""
        test_obj = CommonBase()
        self.assertTrue(test_obj)

    def test_common_server_url(self):
        """Test the setting of attributes using server url."""
        test_obj = CommonBase()
        os.environ['ENV_PREFIX_ATTR3'] = 'attr3_env_value'
        os.environ['ENV_PREFIX_ATTR4'] = 'attr4_env_value'
        # pylint: disable=protected-access
        # pylint: disable=no-member
        test_obj._server_url(
            [
                ('attr1', 'attr1_default_value'),
                ('attr2', 'attr2_default_value'),
                ('attr3', 'attr3_default_value'),
                ('attr4', 'attr4_default_value')
            ],
            'ENV_PREFIX',
            {
                'attr1': 'attr1_kwargs_value',
                'attr3': 'attr3_kwargs_value'
            }
        )
        self.assertEqual(test_obj._attr1, 'attr1_kwargs_value')
        self.assertEqual(test_obj._attr2, 'attr2_default_value')
        self.assertEqual(test_obj._attr3, 'attr3_kwargs_value')
        self.assertEqual(test_obj._attr4, 'attr4_env_value')
        # pylint: enable=no-member
        # pylint: enable=protected-access

    def test_common_server_url_specific(self):
        """Test the setting of attributes using server url."""
        test_obj = CommonBase()
        os.environ['POLICY_PORT'] = '8192'
        os.environ['POLICY_ADDR'] = '127.0.0.1'
        # pylint: disable=protected-access
        # pylint: disable=no-member
        test_obj._server_url(
            [
                ('port', '1234'),
                ('addr', '0.0.0.0'),
                ('path', '/default'),
                ('proto', 'http')
            ],
            'POLICY',
            {
                'port': '5678',
                'proto': 'https'
            }
        )
        self.assertEqual(test_obj._port, '5678')
        self.assertEqual(test_obj._addr, '127.0.0.1')
        self.assertEqual(test_obj._path, '/default')
        self.assertEqual(test_obj._proto, 'https')
        # pylint: enable=no-member
        # pylint: enable=protected-access
        del os.environ['POLICY_PORT']
        del os.environ['POLICY_ADDR']
