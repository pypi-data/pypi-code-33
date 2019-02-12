#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the bundler module."""
from __future__ import absolute_import
from json import loads
from os import unlink, stat
from unittest import TestCase
from random import randint
from tempfile import NamedTemporaryFile
from tarfile import TarFile
from six import PY2
from pacifica.uploader import bundler
from pacifica.uploader.metadata import MetaData, MetaObj


# pylint: disable=too-few-public-methods
class BuildSampleData(object):
    """Build a sample data set to be used in with block."""

    def __init__(self):
        """The the constructor for the object."""
        self.files = []
        self.names = []

    def __enter__(self):
        """Create a set of temporary files to build a bundle."""
        num_files = randint(15, 25)
        for file_i in range(num_files):
            temp_i = NamedTemporaryFile(delete=False)
            uni_str = '\n'.join(
                ['{}: This is the content of {}\n'.format(
                    i, file_i) for i in range(file_i)]
            )
            byte_str = uni_str if PY2 else bytes(uni_str, 'UTF-8')
            temp_i.write(byte_str)
            temp_i.close()
            self.names.append(temp_i.name)
            self.files.append({
                'fileobj': open(temp_i.name, 'r'),
                'name': 'data/data_{}/{}.txt'.format(file_i, file_i),
                'size': stat(temp_i.name).st_size,
                'mtime': stat(temp_i.name).st_mtime
            })
        return self.files

    def __exit__(self, _exc_type, value, traceback):
        """Delete the temporary files."""
        for fname in self.names:
            unlink(fname)
# pylint: enable=too-few-public-methods


class TestBundlerModule(TestCase):
    """Test the bundler module for exported classes."""

    def test_bundler_module(self):
        """Test the bundler stuff."""
        self.assertTrue(bundler.Bundler)

    def test_bundler_basic(self):
        """Test the bundler to stream a tarfile."""
        with BuildSampleData() as sample_files:
            md_obj = MetaData([MetaObj(value='SomethingReal')])
            bundle_fd = NamedTemporaryFile(delete=False)
            bundle = bundler.Bundler(md_obj, sample_files)
            bundle.stream(bundle_fd)
            bundle_fd.close()
            self.assertTrue(bundle_fd)
        check_tar = TarFile(bundle_fd.name, 'r')
        md_fd = check_tar.extractfile('metadata.txt')
        self.assertTrue(md_fd)
        md_bytes = md_fd.read()
        md_str = md_bytes if PY2 else md_bytes.decode('utf8')
        self.assertTrue(loads(md_str))

    def test_bundler_basic_with_cb(self):
        """Test the bundler to stream a tarfile."""
        with BuildSampleData() as sample_files:
            md_obj = MetaData([MetaObj(value='SomethingReal')])
            bundle_fd = NamedTemporaryFile()
            hit_callback = {}
            hit_callback['check'] = False

            def callback(percent):
                """Callback to set the check."""
                hit_callback['check'] = True
                self.assertTrue(percent)
            bundle = bundler.Bundler(md_obj, sample_files)
            bundle.stream(bundle_fd, callback=callback, sleeptime=0)
            self.assertTrue(hit_callback)

    def test_bundler_invalid_hash_algo(self):
        """Test the bundler create with invalid hash algo."""
        md_obj = MetaData([MetaObj(value='1234')])
        hit_exception = False
        try:
            bundler.Bundler(md_obj, [], hashfunc='blarg')
        except ValueError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_bundler_invalid_md_obj(self):
        """Test the bundler create with invalid md object."""
        md_obj = MetaData([MetaObj(value=None)])
        hit_exception = False
        try:
            bundler.Bundler(md_obj, [])
        except ValueError:
            hit_exception = True
        self.assertTrue(hit_exception)
