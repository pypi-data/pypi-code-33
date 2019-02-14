# -*- coding: utf-8 -*-
from re import match
from json import loads as from_json


class ReadConfig:
    def __init__(self, filepath, json=False):
        self.filepath = filepath
        self.json = json
        self.attrib = self.readconfig()
        self.keys = self.attrib.keys()
        for a in self.attrib:
            setattr(self, a.lower(), self.attrib[a.lower()])
            setattr(self, a.upper(), self.attrib[a.upper()])
            setattr(self, a, self.attrib[a])

    def readconfig(self):
        res = {}
        with open(self.filepath) as f:
            data = f.read()
            if self.json:
                res = from_json(data)
                for key in res.keys():
                    res[key.lower()] = res[key]
                    res[key.upper()] = res[key]
            else:
                lines = data.split('\n')  # should make support for \r
                for line in lines:
                    if len(line) > 0:
                        if line[0] == '#':
                            pass
                        else:
                            g = match(r'([\w@,./]+)\s*=\s*([\w@.,\-/:]+)', line)
                            if g:
                                res[(str(g.group(1))).lower()] = str(g.group(2))
                                res[(str(g.group(1))).upper()] = str(g.group(2))
                                res[(str(g.group(1)))] = str(g.group(2))
        if not res:
            raise IOError('Could not read config file, no readable data in it (possibly wrong format)')
        return res

    def __str__(self):
        return 'Configuration object from "%s"' % self.filepath

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return getattr(self, item)
