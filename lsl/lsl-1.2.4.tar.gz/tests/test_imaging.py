# -*- coding: utf-8 -*-

# Python3 compatiability
import sys
if sys.version_info > (3,):
    xrange = range
    
"""Unit test for lsl.imaging modules"""

import os
import copy
import time
import numpy
import shutil
import tempfile
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from lsl import astro
from lsl.common.paths import dataBuild as dataPath
from lsl.imaging import utils
from lsl.imaging import selfCal
from lsl.writer.fitsidi import IDI, NumericStokes
from lsl.sim.vis import srcs as simSrcs
from lsl.common.stations import lwa1, parseSSMIF
from lsl.correlator import uvUtils

run_ms_tests = False
try:
    import casacore
    from lsl.writer.measurementset import MS
    run_ms_tests = True
except ImportError:
    pass

__revision__ = "$Rev: 2650 $"
__version__  = "0.1"
__author__    = "Jayce Dowell"


uvFile = os.path.join(dataPath, 'tests', 'uv-test.fits')
idiFile = os.path.join(dataPath, 'tests', 'idi-test.fits')
idiAltFile = os.path.join(dataPath, 'tests', 'idi-test-alt.fits')
idiSSMIFFile = os.path.join(dataPath, 'tests', 'idi-test-alt.txt')


class imaging_tests(unittest.TestCase):
    """A unittest.TestCase collection of unit tests for the lsl.imaging
    modules."""
    
    testPath = None
    
    def setUp(self):
        """Turn off all numpy warnings and create the temporary file directory."""

        numpy.seterr(all='ignore')
        self.testPath = tempfile.mkdtemp(prefix='test-imaging-', suffix='.tmp')
        
    def test_CorrelatedDataIDI(self):
        """Test the utils.CorrelatedDataIDI class."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedDataIDI(idiFile)
        
        # Dates
        self.assertEqual(idi.dateObs.strftime("%Y-%m-%dT%H:%M:%S"), "2013-03-04T20:36:26")
        
        # Stand and baseline counts
        self.assertEqual(len(idi.stands), 5)
        self.assertEqual(idi.totalBaselineCount, 5*(5+1)/2)
        
        # Basic functions (just to see that they run)
        junk = idi.getAntennaArray()
        junk = idi.getObserver()
        junk = idi.getDataSet(1)
        
        # Error checking
        self.assertRaises(RuntimeError, idi.getDataSet, 2)
        
    def test_CorrelatedDataIDI_MultiIF(self):
        """Test the utils.CorrelatedDataIDI class on a file with multiple IFs."""
        
        # Frequency range
        freq = numpy.arange(0,512)*20e6/512 + 40e6
        # Site and stands
        site = lwa1
        antennas = site.getAntennas()[0:40:2]
        
        # Set baselines and data
        blList = uvUtils.getBaselines(antennas, IncludeAuto=True, Indicies=False)
        visData = numpy.random.rand(len(blList), len(freq))
        visData = visData.astype(numpy.complex64)

        data = {'freq': freq, 'site': site, 'antennas': antennas, 'bl': blList, 'vis': visData}
        
        # Filename and time
        testTime, testFile = time.time(), os.path.join('idi-test-MultiIF.fits')
        
        # Start the file
        fits = IDI(testFile, refTime=testTime, clobber=True)
        fits.setStokes(['xx'])
        fits.setFrequency(data['freq'])
        fits.setFrequency(data['freq']+30e6)
        fits.setGeometry(data['site'], data['antennas'])
        fits.addDataSet(astro.utcjd_to_taimjd(astro.unix_to_utcjd(testTime)), 6.0, data['bl'], 
                          numpy.concatenate([data['vis'], 10*data['vis']], axis=1))
        fits.write()
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(testFile)
        self.assertEqual(idi.freq.size, 2*data['freq'].size)
        dataDict = idi.getDataSet(1, includeAuto=True)
        
        for i in xrange(len(data['bl'])):
            for j in xrange(data['freq'].size):
                self.assertAlmostEqual(dataDict['vis']['xx'][i][j], data['vis'][i,j], 6)
                self.assertAlmostEqual(dataDict['vis']['xx'][i][j+data['freq'].size], 10*data['vis'][i,j], 6)
                
    def test_CorrelatedDataIDI_Alt(self):
        """Test the utils.CorrelatedDataIDI class on a file with an unusual telescope."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedDataIDI(idiAltFile)
        
        # Dates
        self.assertEqual(idi.dateObs.strftime("%Y-%m-%dT%H:%M:%S"), "2013-03-04T20:36:26")
        
        # Stand and baseline counts
        self.assertEqual(len(idi.stands), 5)
        self.assertEqual(idi.totalBaselineCount, 5*(5+1)/2)
        self.assertEqual(idi.integrationCount, 1)
        
        # Basic functions (just to see that they run)
        junk = idi.getAntennaArray()
        junk = idi.getObserver()
        junk = idi.getDataSet(1)
        
        # Error checking
        self.assertRaises(RuntimeError, idi.getDataSet, 2)
        
    def test_CorrelatedDataIDI_AltArrayGeometry(self):
        """Test the utils.CorrelatedDataIDI class on determing array geometry."""
        
        # Open the FITS IDI files
        idi1 = utils.CorrelatedData(idiFile)
        idi2 = utils.CorrelatedData(idiAltFile)
        
        # Dates
        self.assertEqual(idi1.dateObs.strftime("%Y-%m-%dT%H:%M:%S"), idi2.dateObs.strftime("%Y-%m-%dT%H:%M:%S"))
        
        # Stand and baseline counts
        self.assertEqual(len(idi1.stands), len(idi2.stands))
        self.assertEqual(idi1.totalBaselineCount, idi2.totalBaselineCount)
        self.assertEqual(idi1.integrationCount, idi2.integrationCount)
        
        # Check stands
        for s1,s2 in zip(idi1.stands, idi2.stands):
            self.assertEqual(s1, s2)
            
        # Check stations
        station1 = parseSSMIF(idiSSMIFFile)
        station2 = idi2.station
        self.assertAlmostEqual(station1.lat, station2.lat, 3)
        self.assertAlmostEqual(station1.lon, station2.lon, 3)
        self.assertAlmostEqual(station1.elev, station2.elev, 1)
        
        # Check antennas
        ants1 = [a for a in station1.getAntennas() if a.pol == 0]
        ants2 = station2.getAntennas()
        for a1,a2 in zip(ants1, ants2):
            self.assertEqual(a1.id, a2.id)
            self.assertEqual(a1.stand.id, a2.stand.id)
            self.assertAlmostEqual(a1.stand.x, a2.stand.x, 2)
            self.assertAlmostEqual(a1.stand.y, a2.stand.y, 2)
            self.assertAlmostEqual(a1.stand.z, a2.stand.z, 2)
            
    def test_CorrelatedDataUV(self):
        """Test the utils.CorrelatedDataUV class."""
        
        # Open the UVFITS file
        uv = utils.CorrelatedDataUV(uvFile)
        
        # Dates
        self.assertEqual(uv.dateObs.strftime("%Y-%m-%dT%H:%M:%S"), "2013-03-04T20:36:26")
        
        # Stand and baseline counts
        self.assertEqual(len(uv.stands), 5)
        self.assertEqual(uv.totalBaselineCount, 5*(5+1)/2)
        self.assertEqual(uv.integrationCount, 1)
        
        # Basic functions (just to see that they run)
        junk = uv.getAntennaArray()
        junk = uv.getObserver()
        junk = uv.getDataSet(1)
        
        # Error checking
        self.assertRaises(RuntimeError, uv.getDataSet, 2)
        
    def __initData(self):
        """Private function to generate a random set of data for writing a UVFITS
        file.  The data is returned as a dictionary with keys:
         * freq - frequency array in Hz
         * site - lwa.common.stations object
         * stands - array of stand numbers
         * bl - list of baseline pairs in real stand numbers
         * vis - array of visibility data in baseline x freq format
        """

        # Frequency range
        freq = numpy.arange(0,512)*20e6/512 + 40e6
        # Site and stands
        site = lwa1
        antennas = site.getAntennas()[0:40:2]
        
        # Set baselines and data
        blList = uvUtils.getBaselines(antennas, IncludeAuto=True, Indicies=False)
        visData = numpy.random.rand(len(blList), len(freq))
        visData = visData.astype(numpy.complex64)
        
        return {'freq': freq, 'site': site, 'antennas': antennas, 'bl': blList, 'vis': visData}
        
    @unittest.skipUnless(run_ms_tests, "requires the 'casacore' module")
    def test_CorrelatedDataMS(self):
        """Test the utils.CorrelatedDataMS class."""
        
        testTime, testFile = time.time(), os.path.join(self.testPath, 'ms-test-W.ms')
        
        # Get some data
        data = self.__initData()
        
        # Start the table
        tbl = MS(testFile, refTime=testTime)
        tbl.setStokes(['xx'])
        tbl.setFrequency(data['freq'])
        tbl.setGeometry(data['site'], data['antennas'])
        tbl.addDataSet(astro.utcjd_to_taimjd(astro.unix_to_utcjd(testTime)), 6.0, data['bl'], data['vis'])
        tbl.write()
        
        # Open the measurement set
        ms = utils.CorrelatedDataMS(testFile)
        
        # Basic functions (just to see that they run)
        junk = ms.getAntennaArray()
        junk = ms.getObserver()
        junk = ms.getDataSet(1)
        
        # Error checking
        self.assertRaises(IndexError, ms.getDataSet, 2)
        
    @unittest.skipUnless(run_ms_tests, "requires the 'casacore' module")
    def test_CorrelatedDataMS_SingleIF(self):
        """Test the utils.CorrelatedDataMS class on a file with a single IF."""
        
        # Get some data
        data = self.__initData()
        
        # Filename and time
        testTime, testFile = time.time(), os.path.join(self.testPath, 'ms-test-SingleIF.ms')
        
        # Start the file
        fits = MS(testFile, refTime=testTime, clobber=True)
        fits.setStokes(['xx'])
        fits.setFrequency(data['freq'])
        fits.setGeometry(data['site'], data['antennas'])
        fits.addDataSet(astro.utcjd_to_taimjd(astro.unix_to_utcjd(testTime)), 6.0, data['bl'], data['vis'])
        fits.write()
        
        # Open the measurement set
        ms = utils.CorrelatedDataMS(testFile)
        self.assertEqual(ms.freq.size, data['freq'].size)
        ds = ms.getDataSet(1, includeAuto=True)
        
        for i in xrange(len(data['bl'])):
            for j in xrange(data['freq'].size):
                self.assertAlmostEqual(ds['vis']['xx'][i][j], data['vis'][i,j], 6)
                
    def test_sort(self):
        """Test the utils.sortDataDict function."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiFile)
        
        # Get some data to sort
        ds = idi.getDataSet(1, sort=False)
        
        # Sort
        dss = copy.deepcopy(ds)
        utils.sortDataDict(dss)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dss[prop][pol]), len(ds[prop][pol]))
                
    def test_sort_alt(self):
        """Test the utils.sortDataDict function - alternate FITS IDI file."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiAltFile)
        
        # Get some data to sort
        ds = idi.getDataSet(1, sort=False)
        
        # Sort
        dss = copy.deepcopy(ds)
        utils.sortDataDict(dss)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dss[prop][pol]), len(ds[prop][pol]))
                
    def test_sort_uvfits(self):
        """Test the utils.sortDataDict function - UVFITS file."""
        
        # Open the FITS IDI file
        uv = utils.CorrelatedData(uvFile)
        
        # Get some data to sort
        ds = uv.getDataSet(1, sort=False)
        
        # Sort
        dss = copy.deepcopy(ds)
        utils.sortDataDict(dss)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dss[prop][pol]), len(ds[prop][pol]))
                
    def test_prune(self):
        """Test the utils.pruneBaselineRange function."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiFile)
        
        # Get some data to sort
        ds = idi.getDataSet(1)
        
        # Prune
        dsp1 = utils.pruneBaselineRange(ds, uvMin=10)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertTrue(len(dsp1[prop][pol]) < len(ds[prop][pol]))
                
        # Auto-prune
        dsp2 = idi.getDataSet(1, uvMin=10)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dsp1[prop][pol]), len(dsp2[prop][pol]))

        # Auto-prune that should result in no baselines
        dsp3 = idi.getDataSet(1, uvMin=100)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dsp3[prop][pol]), 0)
                
    def test_prune_alt(self):
        """Test the utils.pruneBaselineRange function - alternate FITS IDI file."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiAltFile)
        
        # Get some data to sort
        ds = idi.getDataSet(1)
        
        # Prune
        dsp1 = utils.pruneBaselineRange(ds, uvMin=10)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertTrue(len(dsp1[prop][pol]) < len(ds[prop][pol]))
                
        # Auto-prune
        dsp2 = idi.getDataSet(1, uvMin=10)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dsp1[prop][pol]), len(dsp2[prop][pol]))

        # Auto-prune that should result in no baselines
        dsp3 = idi.getDataSet(1, uvMin=100)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dsp3[prop][pol]), 0)
                
    def test_prune_uvfits(self):
        """Test the utils.pruneBaselineRange function - UVFITS file."""
        
        # Open the FITS IDI file
        uv = utils.CorrelatedData(uvFile)
        
        # Get some data to sort
        ds = uv.getDataSet(1)
        
        # Prune
        dsp1 = utils.pruneBaselineRange(ds, uvMin=10)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertTrue(len(dsp1[prop][pol]) < len(ds[prop][pol]))
                
        # Auto-prune
        dsp2 = uv.getDataSet(1, uvMin=10)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dsp1[prop][pol]), len(dsp2[prop][pol]))

        # Auto-prune that should result in no baselines
        dsp3 = uv.getDataSet(1, uvMin=100)
        for prop in ['bls', 'uvw', 'vis', 'wgt', 'msk', 'jd']:
            for pol in ds['bls'].keys():
                self.assertEqual(len(dsp3[prop][pol]), 0)
                
    def test_rephase(self):
        """Test the utils.rephaseData function."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiFile)
        
        # Get the AntennaArray instance
        aa = idi.getAntennaArray()
        
        # Get some data to sort
        ds = idi.getDataSet(1)
        
        # Rephase #1
        rs1 = utils.rephaseData(aa, ds, currentPhaseCenter='z', newPhaseCenter=simSrcs['Sun'])
        for i in xrange(len(ds['bls']['xx'])):
            self.assertEqual(ds['bls']['xx'][i][0], rs1['bls']['xx'][i][0])
            self.assertEqual(ds['bls']['xx'][i][1], rs1['bls']['xx'][i][1])
            
        # Rephase #2
        rs2 = utils.rephaseData(aa, rs1, currentPhaseCenter=simSrcs['Sun'], newPhaseCenter='z')
        for i in xrange(len(ds['bls']['xx'])):
            self.assertEqual(ds['bls']['xx'][i][0], rs2['bls']['xx'][i][0])
            self.assertEqual(ds['bls']['xx'][i][1], rs2['bls']['xx'][i][1])
            
            for j in xrange(len(ds['vis']['xx'][i])):
                self.assertAlmostEqual(ds['vis']['xx'][i][j], rs2['vis']['xx'][i][j], 2)
                
        # Bad rephase
        self.assertRaises(RuntimeError, utils.rephaseData, aa, ds, currentPhaseCenter='z', newPhaseCenter=simSrcs['vir'])
        
    def test_rephase_alt(self):
        """Test the utils.rephaseData function - alternate FITS IDI file."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiAltFile)
        
        # Get the AntennaArray instance
        aa = idi.getAntennaArray()
        
        # Get some data to sort
        ds = idi.getDataSet(1)
        
        # Rephase #1
        rs1 = utils.rephaseData(aa, ds, currentPhaseCenter='z', newPhaseCenter=simSrcs['Sun'])
        for i in xrange(len(ds['bls']['xx'])):
            self.assertEqual(ds['bls']['xx'][i][0], rs1['bls']['xx'][i][0])
            self.assertEqual(ds['bls']['xx'][i][1], rs1['bls']['xx'][i][1])
            
        # Rephase #2
        rs2 = utils.rephaseData(aa, rs1, currentPhaseCenter=simSrcs['Sun'], newPhaseCenter='z')
        for i in xrange(len(ds['bls']['xx'])):
            self.assertEqual(ds['bls']['xx'][i][0], rs2['bls']['xx'][i][0])
            self.assertEqual(ds['bls']['xx'][i][1], rs2['bls']['xx'][i][1])
            
            for j in xrange(len(ds['vis']['xx'][i])):
                self.assertAlmostEqual(ds['vis']['xx'][i][j], rs2['vis']['xx'][i][j], 2)
                
        # Bad rephase
        self.assertRaises(RuntimeError, utils.rephaseData, aa, ds, currentPhaseCenter='z', newPhaseCenter=simSrcs['vir'])
        
    def test_rephase_uvfits(self):
        """Test the utils.rephaseData function - UVFITS file."""
        
        # Open the UVFITS file
        uv = utils.CorrelatedData(uvFile)
        
        # Get the AntennaArray instance
        aa = uv.getAntennaArray()
        
        # Get some data to sort
        ds = uv.getDataSet(1)
        
        # Rephase #1
        rs1 = utils.rephaseData(aa, ds, currentPhaseCenter='z', newPhaseCenter=simSrcs['Sun'])
        for i in xrange(len(ds['bls']['xx'])):
            self.assertEqual(ds['bls']['xx'][i][0], rs1['bls']['xx'][i][0])
            self.assertEqual(ds['bls']['xx'][i][1], rs1['bls']['xx'][i][1])
            
        # Rephase #2
        rs2 = utils.rephaseData(aa, rs1, currentPhaseCenter=simSrcs['Sun'], newPhaseCenter='z')
        for i in xrange(len(ds['bls']['xx'])):
            self.assertEqual(ds['bls']['xx'][i][0], rs2['bls']['xx'][i][0])
            self.assertEqual(ds['bls']['xx'][i][1], rs2['bls']['xx'][i][1])
            
            for j in xrange(len(ds['vis']['xx'][i])):
                self.assertAlmostEqual(ds['vis']['xx'][i][j], rs2['vis']['xx'][i][j], 2)
                
        # Bad rephase
        self.assertRaises(RuntimeError, utils.rephaseData, aa, ds, currentPhaseCenter='z', newPhaseCenter=simSrcs['vir'])
        
    def test_gridding(self):
        """Test building a image from a visibility data set."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiFile)
        
        # Build the image
        ds = idi.getDataSet(1)
        junk = utils.buildGriddedImage(ds, verbose=False)

        # Error checking
        self.assertRaises(RuntimeError, utils.buildGriddedImage, ds, pol='xy')
        
    def test_gridding_alt(self):
        """Test building a image from a visibility data set - alternate FITS IDI file."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiAltFile)
        
        # Build the image
        ds = idi.getDataSet(1)
        junk = utils.buildGriddedImage(ds, verbose=False)

        # Error checking
        self.assertRaises(RuntimeError, utils.buildGriddedImage, ds, pol='xy')
        
    def test_gridding_uvfits(self):
        """Test building a image from a visibility data set - UVFITS file."""
        
        # Open the UVFITS file
        uv = utils.CorrelatedData(uvFile)
        
        # Build the image
        
        ds = uv.getDataSet(1)
        junk = utils.buildGriddedImage(ds, verbose=False)
        
        # Error checking
        self.assertRaises(RuntimeError, utils.buildGriddedImage, ds, pol='xy')
        
    def test_selfcal(self):
        """Test running a simple self calibration."""
        
        # Open the FITS IDI file
        idi = utils.CorrelatedData(idiFile)
        
        # Go for it!
        aa = idi.getAntennaArray()
        ds = idi.getDataSet(1)
        junk = selfCal.phaseOnly(aa, ds, ds, 173, 'xx', nIter=1, verbose=False)
        
        # Error checking
        self.assertRaises(RuntimeError, selfCal.phaseOnly, aa, ds, ds, 173, 'yx', refAnt=0  )
        self.assertRaises(RuntimeError, selfCal.phaseOnly, aa, ds, ds, 173, 'yx', refAnt=564)
        
    def test_selfcal_alt(self):
        """Test running a simple self calibration - alternate FITS IDI file."""
        
        # Open the alternate FITS IDI file
        idi = utils.CorrelatedData(idiAltFile)
        
        # Go for it!
        aa = idi.getAntennaArray()
        ds = idi.getDataSet(1)
        junk = selfCal.phaseOnly(aa, ds, ds, 173, 'xx', nIter=1, verbose=False)
        
        # Error checking
        self.assertRaises(RuntimeError, selfCal.phaseOnly, aa, ds, ds, 173, 'yx', refAnt=0  )
        self.assertRaises(RuntimeError, selfCal.phaseOnly, aa, ds, ds, 173, 'yx', refAnt=564)
        
    def test_selfcal_uvfits(self):
        """Test running a simple self calibration - UVFITS file."""
        
        # Open the alternate UVFITS file
        uv = utils.CorrelatedData(uvFile)
        
        # Go for it!
        aa = uv.getAntennaArray()
        ds = uv.getDataSet(1)
        junk = selfCal.phaseOnly(aa, ds, ds, 173, 'xx', nIter=1, verbose=False)
        
        # Error checking
        self.assertRaises(RuntimeError, selfCal.phaseOnly, aa, ds, ds, 173, 'yx', refAnt=0  )
        self.assertRaises(RuntimeError, selfCal.phaseOnly, aa, ds, ds, 173, 'yx', refAnt=564)
        
    def tearDown(self):
        """Remove the test path directory and its contents"""

        shutil.rmtree(self.testPath, ignore_errors=True)


class imaging_test_suite(unittest.TestSuite):
    """A unittest.TestSuite class which contains all of the lsl.imaging units 
    tests."""
    
    def __init__(self):
        unittest.TestSuite.__init__(self)
        
        loader = unittest.TestLoader()
        self.addTests(loader.loadTestsFromTestCase(imaging_tests)) 


if __name__ == '__main__':
    unittest.main()
