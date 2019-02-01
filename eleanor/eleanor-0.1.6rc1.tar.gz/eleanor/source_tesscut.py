import numpy as np
from astropy.wcs import WCS
from astropy.table import Table
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import os
import sys
from os.path import join, abspath
import warnings
from . import PACKAGEDIR

import urllib
from .mast import *
from .utils import *

__all__ = ['Source', 'multi_sectors']


def multi_sectors(sectors, tic=None, gaia=None, coords=None):
    """Obtain a list of Source objects for a single target, for each of multiple sectors for which the target was observed.

    Parameters
    ----------
    tic : int, optional
        The TIC ID of the source.
    gaia : int, optional
        The Gaia DR2 source_id.
    coords : tuple, optional
        The (RA, Dec) coords of the object in degrees.
    sectors : list or str
        The list of sectors for which data should be returned, or `all` to return all sectors
        for which there are data.
    """
    objs = []
    if sectors == 'all':
        sectors = list(np.arange(1,3,1, dtype=int))
    if type(sectors) == list:
        for s in sectors:
            star = Source(tic=tic, gaia=gaia, coords=coords, sector=int(s))
            if star.sector is not None:
                objs.append(star)
        if len(objs) < len(sectors):
            warnings.warn('Only {} targets found instead of desired {}. Your '
                          'target may not have been observed yet in these sectors.'
                          ''.format(len(objs), len(sectors)))
        return objs
    else:
        raise TypeError("Sectors needs to be either 'all' or a type(list) to work.")



class Source(object):
    """A single source observed by TESS.

    Parameters
    ----------
    tic : int, optional
        The TIC ID of the source.
    gaia : int, optional
        The Gaia DR2 source_id.
    coords : tuple or astropy.coordinates.SkyCoord, optional
        The (RA, Dec) coords of the object in degrees or an astropy SkyCoord object.
    fn : str, optional
        Filename of a TPF corresponding to the desired source.
    sector : int or str
        The sector for which data should be returned, or `recent` to
        obtain data for the most recent sector which contains this target.

    Attributes
    ----------
    tess_mag : float
        The TESS magnitude from the TIC.
    sector : int
        Sector in which source was observed by TESS.
    camera : int
        TESS camera on which source falls.
    chip : int
        TESS chip on which source falls.
    position_on_chip : (int, int)
        Predicted (x,y) coords of object center on chip.
    postcard : str
        Name of the best postcard (postcard where source should be located closest to the center).
    position_on_postcard : (int, int)
        Predicted (x, y) coords of object center on the above-named postcard.
        Does NOT take into account additional pointing corrections; these will be applied when making the TPF.
    all_postcards : list of strs
        Names of all postcards where the source appears.
    """
    def __init__(self, tic=None, gaia=None, coords=None, fn=None, sector=None, fn_dir=None):
        self.tic     = tic
        self.gaia    = gaia
        self.coords  = coords
        self.fn      = fn
        self.premade = False
        self.usr_sec = sector

        if fn_dir is None:
            self.fn_dir = os.path.join(os.path.expanduser('~'), '.eleanor')
        else:
            self.fn_dir  = fn_dir

        if self.fn is not None:
            try:
                hdu = fits.open(self.fn_dir + '/' + self.fn)
            except:
                assert False, "{0} is not a valid filename or not located in directory {1}".format(fn, fn_dir)
            hdr = hdu[0].header
            self.tic      = hdr['TIC_ID']
            self.tess_mag = hdr['TMAG']
            self.gaia     = hdr['GAIA_ID']
            self.coords   = (hdr['CEN_RA'], hdr['CEN_DEC'])
            self.premade  = True
            self.sector   = hdr['SECTOR']
            self.camera   = hdr['CAMERA']
            self.chip     = hdr['CHIP']
            self.position_on_chip = (hdr['CHIPPOS1'], hdr['CHIPPOS2'])
            self.position_on_postcard = (hdr['POSTPOS1'], hdr['POSTPOS2'])

        else:
            if self.coords is not None:
                if type(self.coords) is SkyCoord:
                    self.coords = (self.coords.ra.degree, self.coords.dec.degree)
                elif (len(self.coords) == 2) & all(isinstance(c, float) for c in self.coords):
                    self.coords  = coords
                else:
                    assert False, ("Source: invalid coords. Valid input types are: "
                                   "(RA [deg], Dec [deg]) tuple or astropy.coordinates.SkyCoord object.")

                self.tic, self.tess_mag, sep, self.tic_version = tic_from_coords(self.coords)
                self.gaia = gaia_from_coords(self.coords)

            elif self.gaia is not None:
                self.coords = coords_from_gaia(self.gaia)
                self.tic, self.tess_mag, sep, self.tic_version = tic_from_coords(self.coords)

            elif self.tic is not None:
                self.coords, self.tess_mag, self.tic_version = coords_from_tic(self.tic)
                self.gaia = gaia_from_coords(self.coords)

            else:
                assert False, ("Source: one of the following keywords must be given: "
                               "tic, gaia, coords, fn.")
                

            self.tess_mag = self.tess_mag[0]





