"""
Source catalog wrapper to quickly look up Ra Dec coordinates of sources.


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

class gammasource():
    """
    A source from my Catalog
    Constructor needs list with informations (splitted line from cat.csv)
    [name, ra, dec, type]
    """
    def __init__(self, info):
        self.name = info[0]
        self.ra = info[1]
        self.dec = info[2]
        self.type = info[3]

    def __repr__(self):
        return "<%s | %s | %s | %s>" % (self.name, self.ra, self.dec, self.type)

    def __str__(self):
        return "%s\ttype = %s\n(Ra %s | Dec %s)" % (self.name, self.type, self.ra, self.dec)

class mypycat():
    """
    a small catalog to store Ra/Dec coordinates of often used sources
    """
    def __init__(self):
        self.cat = self.loadCat()

    def loadCat(self):
        """
        load a csv file with catalog values.
        Syntax i.e.:
        Crab Pulsar;05 34 31.9;+22 00 52.2;PSR
        """
        try:
            home = os.path.join(os.path.expanduser("~"), ".nsb/")
            filepath = os.path.join(home, 'mypycat.txt')
            if not os.path.isfile(filepath):
                self.createMiniCat(filepath)
            catfile = open(filepath, 'r')
            cat = {}
            for line in catfile.readlines():
                if not line.startswith('#'):
                    cat[line.split(';')[0]] = [x for x in line.strip().split(';')]
            return cat

        except IOError as e:
            raise e


    def get(self, source):
        """
        Get a source from the catalog
        input: Source name - will try to find a match in the catalog, user will be asked if multiple are found
        returns: a tevcat.gammasource Object
        """
        source = source.strip()
        candidates = [value for key, value in self.cat.items() if source.lower() in key.lower()]
        if len(candidates) == 1:
            return gammasource(candidates[0])
        elif len(candidates) == 0:
            print('Source not found in catalog!')
            raise KeyError
        else:
            print('found %i sources matching %s:' % (len(candidates), source))
            for i in range(len(candidates)):
                print(str(i) + ') ' + candidates[i][0])
            i = eval(input('which one do you mean?\n'))
            return gammasource(candidates[i])


    def getAll(self):
        """
        Get All sources from the catalog
        returns: a list of cat.gammasource Objects
        """
        sourcelist = []
        for k, v in self.cat.items():
            sourcelist.append(gammasource(v))
        return sourcelist

    #cat = loadCat()

    def createMiniCat(self, filepath):
        print("seems you dont have a source catalog %s" % filepath)
        print("We will create a very minimalistic one. Feel free to add your own sources later (by hand)")
        with open(filepath, 'w') as f:
            f.write("# Name; Ra; Dec; comment\n"
                    "Crab Pulsar;05 34 31.9;+22 00 52.2;PSR\n"
                    "# Moon obviously has no Ra/Dec - this is just a dummy\n"
                    "Moon;00 00 0;00 00 0;none")
        print('SUCCESS! %s was saved to disc\nnow proceeding...\n' % filepath)
