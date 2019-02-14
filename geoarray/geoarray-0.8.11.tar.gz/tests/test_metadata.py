#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
import os
import numpy as np
import tempfile

from geoarray.metadata import GDAL_Metadata
from geoarray import GeoArray
import geoarray


tests_path = os.path.abspath(os.path.join(geoarray.__path__[0], "..", "tests"))


class Test_GDAL_Metadata(TestCase):
    @classmethod
    def setUp(cls):
        cls.test_filePath = os.path.join(tests_path, 'data', 'subset_metadata.bsq')
        cls.tmpOutdir = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmpOutdir.cleanup()

    def test_init(self):
        meta = GDAL_Metadata(self.test_filePath)
        self.assertIsInstance(meta, GDAL_Metadata)

    def test_save(self):
        outPath = os.path.join(self.tmpOutdir.name, 'save_bandnames_from_file.bsq')

        gA = GeoArray(self.test_filePath)
        gA.to_mem()
        gA.bandnames = ['test_%s' % i for i in range(1, gA.bands + 1)]
        gA.save(outPath)

        with open(os.path.splitext(outPath)[0] + '.hdr', 'r') as inF:
            content = inF.read()

        for bN in gA.bandnames.keys():
            self.assertTrue(bN in content, msg="The band name '%s' is not in the written header." % bN)

    def test_save_bandnames(self):
        outPath = os.path.join(self.tmpOutdir.name, 'save_bandnames_from_numpy.bsq')

        gA = GeoArray(np.random.randint(1, 10, (5, 5, 3)))
        gA.bandnames = ['test1', 'band_2', 'layer 3']
        gA.save(outPath)

        with open(os.path.splitext(outPath)[0] + '.hdr', 'r') as inF:
            content = inF.read()

        for bN in gA.bandnames.keys():
            self.assertTrue(bN in content, msg="The band name '%s' is not in the written header. "
                                               "Header contains:  \n\n%s" % (bN, content))
