###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Module that allows to management all the checker Plugins

:author: Stefan-Gabriel CHITIC
'''

from lbCVMFSchecker.PluginLoader import LbLoader


class LbPluginManager():

    def __init__(self, base='lbCVMFSchecker.Plugins'):
        self.loader = LbLoader(base=base)
        self.plugins = self.loader.getModules()

    def reload(self):
        self.loader.reloadPlugins()

    def executeAll(self):
        for plugin_name in self.plugins.keys():
            self.plugins[plugin_name].check()

    def execute(self, plugin):
        self.loader.getModule(plugin).check()
