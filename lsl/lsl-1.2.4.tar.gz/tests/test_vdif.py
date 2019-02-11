# -*- coding: utf-8 -*-

# Python3 compatiability
from __future__ import division

"""Unit test for the lsl.writer.tsfits modules."""

import os
import time
import unittest
import tempfile
import numpy
import pyfits

from lsl.common.paths import dataBuild as dataPath
from lsl.reader import tbw, tbn, vdif as vrdr, errors
from lsl.writer import vdif


__revision__ = "$Rev: 2579 $"
__version__  = "0.2"
__author__    = "Jayce Dowell"

tbwFile = os.path.join(dataPath, 'tests', 'tbw-test.dat')
tbnFile = os.path.join(dataPath, 'tests', 'tbn-test.dat')


class vdif_tests(unittest.TestCase):
    """A unittest.TestCase collection of unit tests for the lsl.writer.vdif
    module."""

    testPath = None

    def setUp(self):
        """Turn off all numpy warnings and create the temporary file directory."""

        numpy.seterr(all='ignore')
        self.testPath = tempfile.mkdtemp(prefix='test-vdif-', suffix='.tmp')

    def __getTBW(self):
        """Private function to load in the test TBW data and get the frames."""

        fh = open(tbwFile, 'rb')

        # Frames 1 through 8
        frames = []
        for i in range(1,9):
            frames.append(tbw.readFrame(fh))

        fh.close()
        return frames

    def __getTBN(self, vanilla=False):
        """Private function to load in the test TBN data and get the frames.  If 
        the keyword 'vanilla' is set to True, gain, sample rate, and frequency meta-
        data are not added to the frames."""

        fh = open(tbnFile, 'rb')

        # Frames 1 through 8
        frames = []
        for i in range(1,9):
            frames.append(tbn.readFrame(fh))

        if not vanilla:
            # Set some values for the other meta-data
            for frame in frames:
                frame.setSampleRate(100000)

        fh.close()
        return frames

    def test_vdif_real(self):
        """Test writing real data to VDIF format."""

        # Setup the file names
        testFile = os.path.join(self.testPath, 'tbw-test-W.fits')

        # Get some data
        frames = self.__getTBW()

        # Write the data
        fh = open(testFile, 'wb')
        for frame in frames:
            vFrame = vdif.Frame(frame.parseID(), frame.getTime(), bits=8, data=frame.data.xy[0,:].astype(numpy.int8))
            vFrame.writeRawFrame(fh)
        fh.close()

        # Read it back in
        fh = open(testFile, 'rb')
        for tFrame in frames:
            vFrame = vrdr.readFrame(fh)
            self.assertAlmostEqual(vFrame.getTime(), tFrame.getTime(), 6)
            for v,t in zip((vFrame.data.data*256-1)/2, tFrame.data.xy[0,:].astype(numpy.int8)):
                self.assertAlmostEqual(v, t, 6)
                
        fh.close()

    def test_vdif_complex(self):
        """Test writing complex data to VIDF format."""

        # Setup the file names
        testFile = os.path.join(self.testPath, 'tbn-test-W.fits')

        # Get some data
        frames = self.__getTBN()
        
        # Write the data
        fh = open(testFile, 'wb')
        for frame in frames:
            stand, pol = frame.parseID()
            if pol == 1:
                continue
            vFrame = vdif.Frame(stand, frame.getTime(), bits=8, data=frame.data.iq)
            vFrame.writeRawFrame(fh)
        fh.close()

        # Read it back in
        fh = open(testFile, 'rb')
        for tFrame in frames[::2]:
            vFrame = vrdr.readFrame(fh)
            for v,t in zip((vFrame.data.data*256-1-1j)/2, tFrame.data.iq):
                self.assertAlmostEqual(v, t, 6)
                
        fh.close()

    def tearDown(self):
        """Remove the test path directory and its contents"""

        tempFiles = os.listdir(self.testPath)
        for tempFile in tempFiles:
            os.unlink(os.path.join(self.testPath, tempFile))
        os.rmdir(self.testPath)
        self.testPath = None


class  vdif_test_suite(unittest.TestSuite):
    """A unittest.TestSuite class which contains all of the lsl.writer.vdif units 
    tests."""
    
    def __init__(self):
        unittest.TestSuite.__init__(self)
        
        loader = unittest.TestLoader()
        self.addTests(loader.loadTestsFromTestCase(vdif_tests)) 


if __name__ == '__main__':
    unittest.main()
