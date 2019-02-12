#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the metadata module."""
from __future__ import absolute_import
from unittest import TestCase
from pacifica.uploader import metadata


class TestModule(TestCase):
    """Test the module for appropriate imports."""

    def test_module(self):
        """Test the metadata module for interface."""
        self.assertTrue(metadata.MetaUpdate)
        self.assertTrue(metadata.MetaData)
        self.assertTrue(metadata.MetaObj)
        self.assertTrue(metadata.metadata_encode)
        self.assertTrue(metadata.metadata_decode)
        self.assertTrue(metadata.FileObj)
