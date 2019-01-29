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
from .__about__ import __shortname__, __version__, __long_description__

class PlatformHelp():
    def __init__(self):
        self.make_title()
        self.make_welcome()
        self.make_requisites()
        self.make_options()

    def make_title(self):
        nameversion = 10 * '#' + 3 * ' ' + __shortname__ + ' v' + __version__ + 3 * ' ' + 10 * '#'
        self.separator = len(nameversion) * '#'
        self.title = nameversion

    def make_welcome(self):
        self.welcome = 'Welcome to ' + __shortname__ + ' (' + __long_description__ + ')\n'

    def make_requisites(self):
        self.requisites = \
            'Requisites: Python 3.5; Scipy; Numpy; Ephem; Astropy; tqdm\n\n'

#
    def make_options(self):
        self.options = \
            '--h --help prints this help message\n\n' + \
            '--create CONFIGFILE\n' + \
            '   writes a standard value configfile \n\n' + \
            'options (can all be set in config):\n' + \
            '--use CONFIGFILE: \n' + \
            '   use an dedicated (non standard) configfile\n' + \
            '--t --time DATETIME: \n' + \
            '   time and date for which the map should be drawn\n' + \
            '   format: 2010/12/24 23:59:59\n' + \
            '--t2 --time_end DATETIME: \n' + \
            '   needed for plots over a timestamp like --trend and --maxnsb\n' + \
            '   format: 2010/12/24 23:59:59\n' + \
            '--o --output /OUTPUT/DIRECTORY/\n' + \
            '   for saving results in different place than working directory\n' + \
            '   filenames will be generated automatically\n' + \
            '--s --size IMAGESIZE:\n' + \
            '   set the output Imagesize in Pixels\n' + \
            '--altaz ALT AZ:\n' + \
            '   set the observation position in the sky manually\n' + \
            '--q --source SOURCENAME:\n' + \
            '   set the observation position automatically on a source by name\n' + \
            '   i.e.: "crab", "moon"\n' + \
            '--l --location LOCATION:\n' + \
            '   The observers coordinates (Lon Lat) on earth and elevation\n' + \
            '   format: 16.5028 -23.27280 1800.0\n' + \
            '--b --brightness NSB zenith brightness:\n' + \
            '   dark night sky zenith brightness in nanoLambert. Needed for model\n' + \
            '   format: 100.0 \n' + \
            '--k EXTINCTION:\n' + \
            '   Extinction in mags per air mass. Needed for model\n' + \
            '   format: 0.55\n' + \
            '--hp LEVEL:\n' + \
            '   HealPix Level for the gaia catalog to be plotted\n' + \
            '   Integer in range [1:12]\n' + \
            '--g --gauss KERNELSIZE:\n' + \
            '   Gaussian Kernel in pixel to smoothen the model images\n' + \
            '   format: 1.5\n' + \
            '\nFlags:\n(to steer programs the behaviour)\n' + \
            '--verbose\n' + \
            '   Do verbose printouts\n' + \
            '--mags\n' + \
            '   use mags per arcsec^2 as output units (instead of nanoLamberts)\n' + \
            '--skymap\n' + \
            '   create the skymap and show it on screen\n' + \
            '--savefits\n' + \
            '   save the Sky-Brightness Map as *.fits file\n' + \
            '--maxnsb VALUE\n' + \
            '   creates a plot of nsb vs. gained observation time. Units nanoLambert.\n' + \
            '   data points are additionally printed to console with --verbose.\n' + \
            '   format: 100.0 \n' + \
            '--trend\n' + \
            '   save the Sky-Brightness Map as *.fits file\n' + \
            '   Source, Sun and Moon Setting/Rising times are printed to console with --verbose\n'

            #
    def show_help(self):
        print(
            self.separator + '\n' + self.title + '\n' + self.separator + '\n' + self.welcome +
            self.requisites + self.options + self.separator)

    def show_title(self):
        print(
            self.separator + '\n' + self.title + '\n' + self.separator)

    def incorrect_parameter(self, parameter):
        print('ERROR. Incorrect parameter: ' + str(parameter))
        self.show_help()

    def date_or_file_input_error(self):
        print('ERROR. File input')
        self.show_help()

    def no_parameters_error(self):
        print('ERROR. No input parameters specified')
        self.show_help()
###
###