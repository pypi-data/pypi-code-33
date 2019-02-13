#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import os
import numpy as np

from astropy.io import fits

__author__ = ['Alan Loh']
__copyright__ = 'Copyright 2018, celespy'
__credits__ = ['Alan Loh']
__license__ = 'MIT'
__version__ = '0.0.1'
__maintainer__ = 'Alan Loh'
__email__ = 'alan.loh@obspm.fr'
__status__ = 'WIP'
__all__ = ['FitsImage']




class FitsImage(object):

    def __init__(self, fitsfile):
        self.fitsfile = fitsfile

    # ================================================================= #
    # ======================== Getter / Setter ======================== #
    @property
    def fitsfile(self):
        """ FITS file
        """
        return self._fitsfile
    @fitsfile.setter
    def fitsfile(self, f):
        f = os.path.abspath(f)

        # Check that the file exists
        assert os.path.isfile(f), "File '{}' not found!".format(f)

        # Check that this is a FITS file
        assert f.lower().endswith('fits'), "A FITS file needs to be provided."

        # Read the header
        self._fitsfile = f
        self._readHeader()

        return

    # ================================================================= #
    # =========================== Internal ============================ #
    def _readHeader(self):
        """ Read the header of the FITS file.
            Store the properties and classifies the data
        """
        self._head = fits.getheader(self.fitsfile)

        # if self._head['NAXIS'] == 2:
        #     # The FITS is an image file
        #     self.type = 'image'
        #     xkw = ['CTYPE1', 'CRPIX1', 'CRVAL1', 'CDELT1', 'CUNIT1']
        #     ykw = ['CTYPE2', 'CRPIX2', 'CRVAL2', 'CDELT2', 'CUNIT2']

        #     # Check that all keywords are present
        #     allkwd = all([k in self._head.keys() for k in xkw + ykw])
        #     assert allkwd, "Fits '{}' is not a standard image.".format(self._fitsfile)

        #     # Get a subset of the header dictionnary
        #     self.xcoord = {k:v for k, v in self._head.items() if k in xkw}
        #     self.ycoord = {k:v for k, v in self._head.items() if k in ykw}

        #     # Get the data
        #     self.data = fits.getdata(self.fitsfile, memmap=True)

        # else:
        #     self.type = 'other'

        try:
            # The FITS is an image file
            self.type = 'image'
            xkw = ['CTYPE1', 'CRPIX1', 'CRVAL1', 'CDELT1', 'CUNIT1']
            ykw = ['CTYPE2', 'CRPIX2', 'CRVAL2', 'CDELT2', 'CUNIT2']

            # Check that all keywords are present
            allkwd = all([k in self._head.keys() for k in xkw + ykw])
            assert allkwd, "Fits '{}' is not a standard image.".format(self._fitsfile)

            # Get a subset of the header dictionnary
            self.xcoord = {k:v for k, v in self._head.items() if k in xkw}
            self.ycoord = {k:v for k, v in self._head.items() if k in ykw}

            # Get the data
            self.data = np.squeeze(fits.getdata(self.fitsfile, memmap=True))

        except:
            self.type = 'other'

        return
