"""
creates a skymap in healpix representation with data from GAIA.


    This work has made use of data from the European Space Agency (ESA)
    mission {\\it Gaia} (\\url{https://www.cosmos.esa.int/gaia}), processed by
    the {\\it Gaia} Data Processing and Analysis Consortium (DPAC,
    \\url{https://www.cosmos.esa.int/web/gaia/dpac/consortium}). Funding
    for the DPAC has been provided by national institutions, in particular
    the institutions participating in the {\\it Gaia} Multilateral Agreement..


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

import os.path
import sys
from operator import itemgetter
import math
import healpy as hp
from nsb.gaia import database_query


def loadCat(level):
    cat = loadFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ducaticat.txt"), level)
    home = os.path.join(os.path.expanduser("~"), ".nsb/")
    catfile = os.path.join(home, "gaiacat.txt")
    if os.path.isfile(catfile):
        cat += loadFile(catfile, level)
    else:
        print('GAIA: No %s found on disc' % catfile)
        i = eval(input('GAIA: Will download the gaia catalog\n'
                       'GAIA: up to which magnitude shall we go?\n'
                       'GAIA: recommended ~15.0 (about 4GB of data) for testing approx 8.0 (about 6MB) will do it...\n'))
        cat += getCat(3.0, i, level) # 14.5
    print('GAIA: now these %i lines have to be sorted! ...' % len(cat))
    cat.sort(key=itemgetter(0))
    return cat


def getCat(magmin, magmax, level):
    try:
        query = database_query.query(magmin, magmax)
        query.submit()
        query.checkStatus()
        data = query.getResult()
        print('GAIA: now processing...')
        catlist = []
        home = os.path.join(os.path.expanduser("~"), ".nsb/")
        catfile = os.path.join(home, "gaiacat.txt")
        with open(catfile, 'a') as f:
            for line in data:
                f.write(line + '\n')
                splitted = line.split(',')
                catlist.append([int(splitted[0]), float(splitted[1]), float(splitted[2]), float(splitted[3]), float(splitted[4])])
                catlist[-1][0] = int(catlist[-1][0] / (2**35 * 4**(12 - level)))
            if len(data) == 3000000:
                print('GAIA: They didnt send us everything. Lets go again.')
                return catlist + getCat(catlist[-1][4], magmax, level)
            else:
                print('GAIA: We got everything.')
                return catlist
    except IOError as e:
        raise e


def loadFile(catalog, level):
    """
    load a txt file with catalog values.
    format:
    source_id,ra,dec,phot_g_mean_flux,phot_g_mean_mag
    """
    try:
        print('GAIA: loading catalog %s from disc...' % catalog)
        catlist = []
        with open(catalog, 'r') as catfile:
            for line in catfile.readlines():
                splitted = line.split(',')
                try:
                    catlist.append([int(splitted[0]), float(splitted[1]), float(splitted[2]), float(splitted[3]), float(splitted[4])])
                    catlist[-1][0] = int(catlist[-1][0] / (2**35 * 4**(12 - level)))
                except Exception as e:
                    print('GAIA: ERROR in ' + str(catalog) + ': '+ str(e))
                    print('GAIA: The problematic line was:\n\t' + str(line))
        return catlist

    except IOError as e:
        raise e


"""
-   HEALpix level 12 = source_id / 34359738368

-   HEALpix level 11 = source_id / 137438953472

-   HEALpix level 10 = source_id / 549755813888

-   HEALpix level n = source_id / 2 ^ 35 * 4 ^ (12 - level)
"""


def binarySearch(value, lis):
    left = 0
    right = len(lis) - 2
    while True:
        if (left > right):
            return left
        test = int((left + right) / 2.0)
        testvalue = lis[test][0]
        if testvalue > value:
            right = test - 1
        elif testvalue < value:
            left = test + 1
        elif testvalue == value:
            return test


def getAllwithIndex(listindex, cat):
    lower = listindex
    upper = listindex
    while cat[lower][0] == cat[listindex][0]:
        lower -= 1
        if lower < 0:
            break
    while cat[upper][0] == cat[listindex][0]:
        upper += 1
        if upper > len(cat) - 1:
            break
    return cat[lower + 1: upper]


def getTotalFlux(healpixid, cat):
    """
    Get the Flux in that specific healpixel
    """
    seed = binarySearch(healpixid, cat)
    stars = getAllwithIndex(seed, cat)

    flux = 0.0
    for source in stars:
        flux += source[3]
    return flux, len(stars)


def getSurfaceBrightness(flux, area):
    if flux > 0:
        m = -2.5 * math.log10(flux) + 25.5248
        return m + 2.5 * math.log10(area)
    else:
        return 100.0


def createMap(level):
    cat = loadCat(level)
    catalogname = 'healpixmap_level' + str(level) + '.txt'
    home = os.path.join(os.path.expanduser("~"), ".nsb/")
    filepath = os.path.join(home, catalogname)
    print('GAIA: now creating ' + filepath)
    with open(filepath, 'w') as f:
        pixel = hp.nside2npix(2**level)
        for healpixid in range(pixel):
            ra, dec = hp.pix2ang(2**level, healpixid, nest=True, lonlat=True)
            deg2 = hp.nside2pixarea(2**level, degrees=True)
            arcsec2 = deg2 * 60**2 * 60**2
            flux, number = getTotalFlux(healpixid, cat)
            brightness = getSurfaceBrightness(flux, arcsec2)
            f.write(str(healpixid) + ', ' +
                    str(ra) + ', ' +
                    str(dec) + ', ' +
                    str(flux) + ', ' +
                    str(brightness) + ', ' +
                    str(arcsec2) + ', ' +
                    str(number) + '\n')
    print("GAIA: Succesfully created " + catalogname)


# Here comes the main
if __name__ == '__main__':
    level = int(sys.argv[1])
    createMap(level)
    print('GAIA: done.')

