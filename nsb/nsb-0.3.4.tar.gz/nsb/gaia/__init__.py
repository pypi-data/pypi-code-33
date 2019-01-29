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
import healpy as hp
from ..gaia import create
from tqdm import tqdm


class Gaia(object):
    """docstring for gaia"""
    def __init__(self, level):
        self.level = level
        try:
            catalogname = 'healpixmap_level' + str(self.level) + '.txt'
            home = os.path.join(os.path.expanduser("~"), ".nsb/")
            filepath = os.path.join(home, catalogname)
            self.loadMap(filepath)
        except Exception as e:
            print('GAIA: ' + str(e))
            print('GAIA: Seems there is no gaia healpixmap with level %i.\n'
                  'GAIA: We will create a new one and try again.\n'
                  'GAIA: This might take a while...' % level)
            create.createMap(self.level)
            self.loadMap(filepath)
            # raise SystemExit

    def loadMap(self, filepath):
        print('GAIA: Opening gaia catalog map...\t(reduce heaplix level if slow)')
        f = open(filepath)
        self.map = []
        for line in tqdm(f.readlines(), mininterval=0.5):
            self.map.append([float(x) for x in line.split(',')])
        f.close()

    def healpix(self, ra, dec):
        return hp.ang2pix(2**self.level, ra, dec, nest=True, lonlat=True)

    def getBrightness(self, healpixid):
        return self.map[healpixid][4]

    def getFlux(self, healpixid):
        return self.map[healpixid][3]

    def getRa(self, healpixid):
        return self.map[healpixid][1]

    def getDec(self, healpixid):
        return self.map[healpixid][2]

    def getArcsec2(self, healpixid):
        return self.map[healpixid][5]

    def getNumber(self, healpixid):
        return self.map[healpixid][6]
