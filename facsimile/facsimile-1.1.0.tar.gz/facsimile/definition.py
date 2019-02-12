#!/usr/bin/env python
##########################################################################

import os
import collections

from . import codec
from munge import util


class Definition(collections.MutableMapping):

    """ Package and instance definition only, no state info """

    def __init__(self, fax):
        self.data_ext = None

        self._fax = fax

        self.__modules = []
        self.__def = {}

    def _load(self):
        fax = self._fax

        for each in self.def_file_list():
            if not self.data_ext:
                self.data_ext = os.path.splitext(each[1])[1].lstrip('.')
            self.add_definition(*each)

        # TODO - remove from legacy
        if not self.__modules:
            self.__modules = self._fax.load_datafile("modules", default=[])

        for each in self._fax.find_datafile("install", os.path.join(fax.src_dir, "config")):
            self.add_definition(*each)

    def add_definition(self, codec, def_file):
        self._fax.debug_msg("adding definition %s" % def_file)
        data = open(def_file).read()
        homedir = os.getenv('HOME')
        user = os.getenv('USER')
        data = data.replace('%HOMEDIR%', homedir)
        # tmp til proper tmpl render
        data = data.replace('{{environ.HOME}}', homedir)
        data = data.replace('{{environ.USER}}', user)
        util.recursive_update(self.__def, codec().loads(data), merge_lists=False)
        #print "LOADED: [%s]" % def_file, self.__def

    def def_list(self):
        fax = self._fax
        return ['facsimile', self._fax.name] + fax.release_environment.split('.')

    def def_file_list(self):
        define_dir = self._fax.define_dir

        # make sure we're not loading before source checkout
        # this should go away once bootstrapping is in
        if not os.path.exists(define_dir):
            raise IOError("define dir '%s' does not exist" % (define_dir,))

        rv = []
        for each in self.def_list():
            files = self._fax.find_datafile(each, define_dir)
            rv.extend(files)

        if not rv:
            raise IOError("unable to open definition file '%s' in %s" % (each, define_dir))

        return rv

    @property
    def data(self):
        if not self.__def:
            self._load()

        return self.__def

    def modules(self):
        if not self.__modules:
            self.__modules = self._fax.load_datafile("modules", default=[])
        return self.__modules

    def __getitem__(self, key):
        if not self.__def:
            self._load()
        return self.__def[key]

    def __setitem__(self, key, value):
        raise TypeError("Definition is immutable")

    def __delitem__(self, key):
        raise TypeError("Definition is immutable")

    def __iter__(self):
        if not self.__def:
            self._load()
        return iter(self.__def)

    def __len__(self):
        if not self.__def:
            self._load()
        return len(self.__def)

##########################################################################
