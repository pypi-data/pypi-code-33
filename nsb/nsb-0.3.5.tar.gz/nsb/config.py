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

import os

from .nsbtools import makeDate



class TheConfiguration():
    def __init__(self):
        pass

    def readStandardConfig(self):
        try:
            home = os.path.join(os.path.expanduser("~"), ".nsb/")
            self.config_filepath = os.path.join(home,'config.cfg')
            self.readConfig(self.config_filepath)
        except Exception as e:
            print('%s not found! \nWill now try to create a default one!' % self.config_filepath)
            print(e)
            self.createConfig(self.config_filepath)
            self.readConfig(self.config_filepath)

    def readConfig(self, configfile):
        self.file = open(configfile, 'r')
        self.config = {}
        try:
            for line in self.file:
                line = line.strip()
                if not line.startswith('#'):
                    self.config[line.split('=')[0].strip()] = line.split('=')[1].strip()
            t1, t2 = self.config['time'].split(' ')[0], self.config['time'].split(' ')[1]
            self.config['time'] = makeDate(t1, t2)
            print('successfully opened %s' % configfile)
        except Exception as e:
            print('\nSomething went wrong while reading %s' % configfile)
            print(e)
            pass
        self.file.close()

    def createConfig(self, configfile):
        with open(configfile, 'w+') as f:
            f.write("# allskymaps Config File\n"
                    "#\n"
                    "# Date and Time\n"
                    "time = today now\n"
                    "#time = 2017/01/18 23:30:00\n"
                    "#\n"
                    "# Observer Location (HESS is at 16.5028 -23.27280 @ 1800.0)\n"
                    "Lon = 16.5028\n"
                    "Lat = -23.27280\n"
                    "elevation = 1800.\n"
                    "#\n"
                    "# dark zenith night sky brightness (units nanoLambert)\n"
                    "B = 77.0\n"
                    "#\n"
                    "# Extinction coefficient (units mags per air mass)\n"
                    "k = 0.479\n"
                    "#\n"
                    "# define output units mag/arcsec^2 (instead of nanoLamberts)\n"
                    "use_mag = False\n"
                    "#\n"
                    "# output Imagesize in Pixels (its gonna be square)\n"
                    "image_size = 200\n"
                    "#\n"
                    "# observation position in the sky [deg]\n"
                    "alt = 90.0\n"
                    "az  = 0.0\n"
                    "#\n"
                    "# Level of HealPixMap used for plotting gaia catalog\n"
                    "healpixlevel = 7\n"
                    "#\n"
                    "# Gaussian smoothing kernel [pixel]\n"
                    "gauss = 0.0\n"
                    "#\n"
                    "moon_above_horizon = 0.0\n"
                    "#\n"
                    "sun_below_horizon = -18.0\n"
                    "#\n"
                    "source_above_horizon = 10.0\n")

        print('SUCCESS! %s with default values was saved to disc\nnow proceeding...\n' % os.path.realpath(configfile))
