#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import numpy as np

from astropy.wcs import WCS
from matplotlib import pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from .data import FitsImage

__author__ = ['Alan Loh']
__copyright__ = 'Copyright 2018, celespy'
__credits__ = ['Alan Loh']
__license__ = 'MIT'
__version__ = '0.0.1'
__maintainer__ = 'Alan Loh'
__email__ = 'alan.loh@obspm.fr'
__status__ = 'WIP'
__all__ = ['Image']


class Image(FitsImage):

    def __init__(self, fitsfile):
        FitsImage.__init__(self, fitsfile)
        self.xsize = 10
        self.ysize = 10 
        self.cmap  = 'Blues'
        self.mode  = 'linear'
        self.vmin  = None
        self.vmax  = None
        self.xmin  = None
        self.xmax  = None
        self.ymin  = None
        self.ymax  = None
        self.xformat = 'hh:mm:ss'
        self.yformat = 'dd:mm:ss'
        self.xlabel = self.xcoord['CTYPE1']
        self.ylabel = self.ycoord['CTYPE2'] 
        self.clabel = ''

    # ================================================================= #
    # ======================== Getter / Setter ======================== #

    def plot(self, **kwargs):
        """ Plot the image
        """
        self._initFigure(**kwargs)

        self._plotImage()

        #self._plotContour()

        return

    # ================================================================= #
    # =========================== Internal ============================ #
    def _initFigure(self, **kwargs):
        """ Initialize the figure environement.
            It will also compute the correct tranformation using WCS
        """
        self._evalkwargs(kwargs)
        self.fig = plt.figure( figsize=(self.xsize/2.54, self.ysize/2.54) )

        self.wcs = WCS(naxis=2)
        self.wcs.wcs.crpix = [self.xcoord['CRPIX1'], self.ycoord['CRPIX2']]
        self.wcs.wcs.crval = [self.xcoord['CRVAL1'], self.ycoord['CRVAL2']]
        self.wcs.wcs.cdelt = [self.xcoord['CDELT1'], self.ycoord['CDELT2']]
        self.wcs.wcs.ctype = [self.xcoord['CTYPE1'], self.ycoord['CTYPE2']]
        self.wcs.wcs.cunit = [self.xcoord['CUNIT1'], self.ycoord['CUNIT2']]
        
        plt.subplot(1, 1, 1, projection=self.wcs)
        self.ax = plt.gca()

    def _setLimits(self):
        if self.mode == 'log':
            if self.vmin is None:
                self.vmin = np.max( (np.min( self.data[self.data > 0] ), np.max(self.data)) )
            if self.vmax is None:
                self.vmax = np.max(self.data) 
            self.normcb = mpl.colors.LogNorm(vmin=self.vmin, vmax=self.vmax)
        elif self.mode == 'linear':
            if self.vmin is None:
                self.vmin = np.min(self.data)
            if self.vmax is None:
                self.vmax = np.max(self.data) 
            self.normcb = mpl.colors.Normalize(vmin=self.vmin, vmax=self.vmax)
        else:
            print("\t=== Mode '{}' unrecognized ===".format(self.mode))
            return
        # if self.xmin is None:
        #     self.extent = None
        # else:
        #     self.extent = [self.xmin, self.xmax, self.ymin, self.ymax]
        # self.extent = [self.xmin, self.xmax, self.ymin, self.ymax]

    def _plotImage(self):
        """ Add the image
        """
        self._setLimits()
        self.im = plt.imshow(self.data, origin='lower', cmap=self.cmap,
            interpolation='nearest', norm=self.normcb)
            #, extent=self.extent, interpolation='nearest', )#, rasterized=self.raster)        
        self._colorBar()
        self._finalDisplay()
        plt.show()
        #self._showPSF()
        #self._fancyDisplay()
        return

    def _plotContour(self):
        """ Add the contours
        """
        self._setLimits()
        x = np.arange(self.data.shape[0])
        y = np.arange(self.data.shape[1])
        X, Y = np.meshgrid(x, y)
        self.im  = plt.contourf(X, Y, self.data, 10, cmap=self.cmap)#, linewidths=0.2)
        for c in self.im.collections:
            c.set_edgecolor('face')
        self._colorBar()
        #self._showPSF()
        self._finalDisplay()
        plt.show()
        return

    def _colorBar(self):
        """ Add a colorbar on the right part of the figure
        """
        cax  = inset_axes(self.ax, width="3%", height="100%", loc=2, 
            bbox_to_anchor=(1.05, 0, 1, 1), bbox_transform=self.ax.transAxes, borderpad=0)
        cbar = plt.colorbar(cax=cax, orientation='vertical')
        cbar.solids.set_edgecolor('face')
        if self.clabel == '':
            try:
                self.clabel = r'{} ({})'.format(self._head['BTYPE'].title(), self._head['BUNIT'].title())
            except:
                pass
        cbar.set_label(self.clabel)
        return

    def _finalDisplay(self):
        """
        """
        self.ax.coords[0].set_major_formatter(self.xformat)
        self.ax.coords[1].set_major_formatter(self.yformat)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        return

    def _evalkwargs(self, kwargs):
        """ Read the kwargs arguments, 
            fill the properties if needed. 
        """
        for key, value in kwargs.items():
            if   key == 'xsize': self.xsize = value
            elif key == 'ysize': self.ysize = value
            elif key == 'cmap':  self.cmap  = value
            elif key == 'mode':  self.mode  = value
            elif key == 'vmin':  self.vmin  = value
            elif key == 'vmax':  self.vmax  = value
            elif key == 'xmin':  self.xmin  = value
            elif key == 'xmax':  self.xmax  = value
            elif key == 'ymin':  self.ymin  = value
            elif key == 'ymax':  self.ymax  = value
            elif key == 'xlabel':  self.xlabel  = value
            elif key == 'ylabel':  self.ylabel  = value
            elif key == 'clabel':  self.clabel  = value
            elif key == 'xformat': self.xformat = value
            elif key == 'yformat': self.yformat = value
            else:
                pass
        return


