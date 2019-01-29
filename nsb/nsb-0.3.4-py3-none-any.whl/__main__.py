#!/usr/bin/env python3
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


import sys
import inspect
import ephem
import os.path
import math

from .help import PlatformHelp
from .input_options import ReadOptions
from .fitsimage import FitsImage
from .config import TheConfiguration
from .nsbtools import makeDateString, plotMaps
from .mypycat import mypycat
from .gaia import Gaia
from .brightness import Brightness


def main():
    home = os.path.join(os.path.expanduser("~"), ".nsb/")
    if not os.path.exists(home):
        os.makedirs(home)

    Help = PlatformHelp()
    Options = ReadOptions(sys.argv)
    try:
        assert(Options.show_help == False)
    except:
        print(inspect.stack()[0][2:4][::-1])
        # Show help and halt
        Help.show_help()
        raise SystemExit

    Help.show_title()
    Configuration = TheConfiguration()
    if Options.altconfset:
        Configuration.readConfig(Options.conf)
    else:
        Configuration.readStandardConfig()

    # Lets have a look what we gonna do today...

    # try to get all the values from user input (Options)
    # if it fails, because there was no input -> use the values from Configfile.

    try:
        size = Options.imageSize
        print('* user input: Imagesize of %i pixels' % size)
    except Exception as e:
        size = int(Configuration.config['image_size'])
        print('* Imagesize of %i pixels from config file' % size)
    try:
        if Options.source_set:
            mpc = mypycat()
            source = mpc.get(Options.tracked_source_name)
            alt, az = 0, 0 # has to be calculated later
            print('* user input: pointing on %s' % source.name)
        else:
            alt = Options.alt
            az = Options.az
            source = None
            print('* user input: Alt/Az of %.1f|%.1f' % (alt, az))
    except Exception as e:
        alt = float(Configuration.config['alt'])
        az = float(Configuration.config['az'])
        source = None
        print('* Alt/Az of %.1f|%.1f from config file' % (alt, az))
    try:
        level = Options.healpixlevel
        print('* user input: HealPixLevel of %i' % level)
    except Exception as e:
        level = int(Configuration.config['healpixlevel'])
        print('* HealPixLevel of %i from config file' % level)
    try:
        lat, lon = float(Options.lat), float(Options.lon)
        print('* user input location: Lat %s Lon %s' % (lat, lon))
    except Exception as e:
        lat, lon = float(Configuration.config['Lat']), float(Configuration.config['Lon'])
        print('* location from config file: Lat %s Lon %s' % (lat, lon))
    try:
        elevation = float(Options.elevation)
        print('* user input elevation: %.1f m ' % elevation)
    except Exception as e:
        elevation = float(Configuration.config['elevation'])
        print('* elevation from config file: %.1f m' % elevation)
    try:
        B_zero = Options.B_zero
        print('* user input B_zero = %.3f' % B_zero)
    except Exception as e:
        B_zero = float(Configuration.config['B'])
        print('* B_zero = %.3f from config file ' % B_zero)
    try:
        k = Options.extinction
        print('* user input k=%.3f' % k)
    except Exception as e:
        k = float(Configuration.config['k'])
        print('* Extinction from config file k=%.3f' % k)
    try:
        gauss = Options.gauss
        if gauss > 0:
            print('* user input gaussian smoothing with %.1f' % gauss)
        else:
            print('* no smoothing')
    except Exception as e:
        gauss = float(Configuration.config['gauss'])
        if gauss > 0:
            print('* Gaussian smoothing with %.1f from config' % gauss)
        else:
            print('* no smoothing')
    try:
        use_mag = Options.use_mag
        print('* user input units mag/arcsec^2')
    except Exception as e:
        um = Configuration.config['use_mag']
        if um in ('True', 'true', '1', 'yes', 'Yes', 't', 'T'):
            use_mag = True
        else:
            use_mag = False
        print('* units specified in config file: use_mag = %s' % use_mag)
    try:
        output_dir = Options.output_dir
        print('* user specified output to: %s' % output_dir)
    except Exception as e:
        output_dir = ""
    try:
        date_and_time = ephem.Date(Options.time)
        print('* user input Date of %s' % date_and_time)
    except Exception as e:
        date_and_time = ephem.Date(Configuration.config['time'])
        print('* Date from config file %s' % date_and_time)

    try:
        date_and_time2 = ephem.Date(Options.time2)
        print('* user input End Date of %s' % date_and_time2)

    except Exception as e:
        date_and_time2 = date_and_time + 0.5
        if Options.obs_time or Options.trend:
            print('* NO END TIME set. Going to use start + 12 hours')

    """
    Let the Drawing begin!
    """
    if Options.obs_time and Options.trend:
        if date_and_time2 < date_and_time:
            print(" time_end has to be after time_start! - No Observation time gain Plot possible.")
        else:
            if date_and_time + 360 > date_and_time2:
                input("\nDoing the max NSB Observation time gain plot makes more sense with a timespan\nof more than one year...\n[Enter] to continue anyway\n")
            brt = Brightness(Options, Configuration, date_and_time, date_and_time2, source, level, threshold=Options.limit, timeresolution=1)
            brt.calculate()
            brt.plotObsTime()
            brt.plotTimespan()


    if Options.obs_time and (not Options.trend):
        if date_and_time2 < date_and_time:
            print(" time_end has to be after time_start! - No Observation time gain Plot possible.")
        else:
            if date_and_time + 360 > date_and_time2:
                input("\nDoing the max NSB Observation time gain plot makes more sense with a timespan\nof more than one year...\n[Enter] to continue anyway\n")
            brt = Brightness(Options, Configuration, date_and_time, date_and_time2, source, level, threshold=Options.limit, timeresolution=1)
            brt.calculate()
            brt.plotObsTime()

    if (not Options.obs_time) and Options.trend:
        if date_and_time2 < date_and_time:
            print(" time_end has to be after time_start! - No Observation time gain Plot possible.")
        else:
            brt = Brightness(Options, Configuration, date_and_time, date_and_time2, source, level, threshold=None, timeresolution=15)
            brt.calculate()
            brt.plotTimespan()
    if Options.skymap:

        Image_allsky = FitsImage(size, 90.0, 0.0, None, lon, lat, elevation, date_and_time, B_zero, k, use_mag)
        print("* Moon at \tzen %.2f\taz %.2f\twith a phase of %.2f %% (%.2f deg)" % (
              math.degrees(Image_allsky.zen_moon), math.degrees(Image_allsky.az_moon), 100 * Image_allsky.moon.moon_phase,
              math.degrees(Image_allsky.moon_alpha)))

        gaiamap = Gaia(level)
        Image_allsky.drawModel(gaiamap)
        if gauss > 0:
            Image_allsky.smooth_gauss(sigma=gauss)

        median, mean = Image_allsky.getStatistics()
        print('Median All-Sky Brightness: \t %.2f %s\n'
              'Mean All-Sky Brightness: \t %.2f %s' % (median, Image_allsky.units, mean, Image_allsky.units))

        if Options.savefits:

            Image_allsky.fitsfile.writeto(output_dir
                                          + "NSB_of_"
                                          + makeDateString(date_and_time)
                                          + "_All-Sky.fits", 'exception', True)

        plotMaps([Image_allsky]) #Image_FOV]),

    print("done.\n")



if __name__ == '__main__':
    main()
