"""
allskymaps python package.

Draws Allsky Nightsky Images with stars from the GAIA catalog

    This work has made use of data from the European Space Agency (ESA)
    mission {\\it Gaia} (\\url{https://www.cosmos.esa.int/gaia}), processed by
    the {\\it Gaia} Data Processing and Analysis Consortium (DPAC,
    \\url{https://www.cosmos.esa.int/web/gaia/dpac/consortium}). Funding
    for the DPAC has been provided by national institutions, in particular
    the institutions participating in the {\\it Gaia} Multilateral Agreement.

and draws moonlight corresponding to the Model from Krisciunas et al.

   author = {{Krisciunas}, K. and {Schaefer}, B.~E.},
    title = "{A model of the brightness of moonlight}",
  journal = {\pasp},
     year = 1991,
    month = sep,
   volume = 103,
    pages = {1033-1039},
      doi = {10.1086/132921},
   adsurl = {http://adsabs.harvard.edu/abs/1991PASP..103.1033K},


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Created and maintained by Matthias Buechele [FAU].

"""

import numpy as np
import astropy.io.fits as pyfits
import ephem
import math
from scipy.ndimage import gaussian_filter, median_filter
from tqdm import tqdm

from .nsbtools import greatCircle, B_moon, B_sky, MagnLb, nLbMag



class FitsImage():
    def __init__(self, size, alt, az, source, lon, lat, elevation, date_and_time, B_zero, k, use_mag):
        # create an empty FITS HDU with size x size for storing the model values
        self.imagesize = size
        a = np.empty((self.imagesize, self.imagesize))
        a.fill(np.nan)
        self.fitsfile = pyfits.PrimaryHDU(a)
        # create an PyEphem Observer and set the pressure to 0 -> No atmospheric corrections near the horizon
        self.site = ephem.Observer()
        self.site.pressure = 0
        self.site.elevation = elevation
        self.site.lon, self.site.lat = math.radians(lon), math.radians(lat)
        self.site.date = date_and_time

        self.moon = ephem.Moon()
        self.sun = ephem.Sun()
        self.moon.compute(self.site)
        self.sun.compute(self.site)

        self.zen_moon = np.pi / 2 - self.moon.alt
        self.az_moon = self.moon.az
        self.moon_alpha = math.acos(self.moon.moon_phase * 2 - 1)

        # all the other stuff
        self.resolution = math.radians(180) / size
        self.B_zero = B_zero
        self.k = k
        self.use_mag = use_mag

        if not source == None:
            pointing = source.name
            if source.name.lower().strip() == 'moon':
                self.alt = self.moon.alt
                self.az = self.moon.az
            else:
                self.source = ephem.FixedBody()
                self.source._ra, self.source._dec = source.ra, source.dec
                self.source.name = source.name
                self.source.compute(self.site)
                self.alt = self.source.alt
                self.az = self.source.az
                print('* %s at \tzen %.2f\taz %.2f' % (self.source.name, math.degrees(np.pi/2 - self.alt), self.az))
        else:
            pointing = 'n.a.'
            self.alt = math.radians(alt)
            self.az = math.radians(az)

        self.fitsfile.header['sunalt'] = (math.degrees(self.sun.alt), 'Degrees')
        self.fitsfile.header['moonalt'] = (math.degrees(self.moon.alt), 'Degrees')
        self.fitsfile.header['moonaz'] = (math.degrees(self.moon.az), 'Degrees')
        self.fitsfile.header['moonph'] = (self.moon.moon_phase, 'Moon Phase as Fraction of illuminated Surface')
        self.fitsfile.header['alt'] = (math.degrees(self.alt), 'Degrees (Pointing)')
        self.fitsfile.header['az'] = (math.degrees(self.az), 'Degrees (Pointing)')
        self.fitsfile.header['source'] = (pointing, 'Name of pointed source (if available)')
        self.fitsfile.header['extinc'] = (self.k, 'Extincion Coefficient')
        self.fitsfile.header['bzero'] = (self.B_zero, 'Zenith brightness without moon')
        self.fitsfile.header['lat'] = (str(self.site.lat), 'Observer GPS Position')
        self.fitsfile.header['lon'] = (str(self.site.lon), 'Observer GPS Position')
        self.fitsfile.header['elev'] = (self.site.elevation, 'Observer Elevation [m above NN]')
        if self.use_mag:
            self.units = 'mag/arcsec^2'
        else:
            self.units = 'nLb'
        self.fitsfile.header['units'] = (self.units)


    def drawModel(self, gaiamap):
        sunalt = float(self.sun.alt)
        if sunalt > 0:
            sunset = self.site.next_setting(self.sun)
            # print fancy red error message
            message = 5 * '#' + ' Sun still up! Next sunset at %s ' % sunset + 5 * '#'
            print('\x1b[0;30;41m' + len(message) * '#')
            print(message)
            print(len(message) * '#' + '\x1b[0m')
            a = np.empty((self.imagesize, self.imagesize))
            a.fill(-1)
            self.fitsfile = pyfits.PrimaryHDU(a)
        elif sunalt < 0 and sunalt > math.radians(-18.0):
            # print fancy red error message
            message = 5 * '#' + ' Sunlight might have influence! sun alt= %.2f deg ' % math.degrees(sunalt) + 5 * '#'
            print('\x1b[0;30;41m' + len(message) * '#')
            print(message)
            print(len(message) * '#' + '\x1b[0m')
            a = np.zeros((self.imagesize, self.imagesize))
            self.fitsfile = pyfits.PrimaryHDU(a)
        else:
            offset_zen = float(np.pi/2 - self.alt)
            offset_az = float(self.az)
            offset_x = 0
            offset_y = -offset_zen * (1  /self.resolution)

            self.gaiamap = gaiamap

            print('Drawing Model...\t\t(reduce imagesize if slow)')
            # Model drawing starts here:
            self.fitsfile.header['ismodel'] = ('True', 'either Model or measurement')
            for x in tqdm(range(self.imagesize)):
                for y in range(self.imagesize):
                    az = (math.atan2((x - self.imagesize / 2. - offset_x),
                                     (y - self.imagesize / 2. - offset_y)) + offset_az)
                    zen = math.hypot((x - self.imagesize / 2. - offset_x),
                                     (y - self.imagesize / 2. - offset_y)) * self.resolution
                    moondist = greatCircle(zen, az, self.zen_moon, self.az_moon)
                    ra, dec = self.site.radec_of(az, math.pi / 2 - zen)
                    healpixid = self.gaiamap.healpix(math.degrees(ra), math.degrees(dec))
                    if (zen > math.radians(90.0)):
                        continue
                    else:
                        if self.use_mag:
                            if moondist > math.radians(5.0):
                                self.fitsfile.data[y, x] = nLbMag(
                                    B_moon(zen, az, self.zen_moon, self.az_moon, self.k, self.moon_alpha) +
                                    B_sky(zen, az, self.B_zero, self.k) +
                                    MagnLb(self.gaiamap.getBrightness(healpixid)))
                        else:
                            if moondist > math.radians(5.0):
                                self.fitsfile.data[y, x] = (
                                B_moon(zen, az, self.zen_moon, self.az_moon, self.k, self.moon_alpha) +
                                B_sky(zen, az, self.B_zero, self.k) +
                                MagnLb(self.gaiamap.getBrightness(healpixid)))

    def smooth_gauss(self, sigma):
        self.fitsfile.data = gaussian_filter(self.fitsfile.data, sigma=sigma)

    def median_filter(self, size):
        self.fitsfile.data = median_filter(self.fitsfile.data, size=int(size))

    def getStatistics(self):
        median, mean = np.nanmedian(self.fitsfile.data), np.nanmean(self.fitsfile.data)
        if not np.isnan(median) and not np.isnan(mean):
            self.fitsfile.header['median'] = (median, 'Median Image Brightness')
            self.fitsfile.header['mean'] = (mean, 'Mean Image Brightness')
        return median, mean
#
#
