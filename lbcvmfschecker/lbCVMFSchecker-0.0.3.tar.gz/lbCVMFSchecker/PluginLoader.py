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

Module that allows to load all the checker Plugins

:author: Stefan-Gabriel CHITIC
'''

import os
from LbCVMFSCheckerPluginBase import PluginBase


class LbLoader(object):

    def __init__(self, base='lbCVMFSchecker.Plugins'):
        self.base = base
        self.reloadPlugins()

    def getPluginNames(self):
        return self.pluginNames

    def getModules(self):
        return self.plugins

    def getModule(self, name):
        if not self.plugins.get(name, None):
            raise ImportError('No module %s loaded' % name)
        return self.plugins[name]

    def reloadPlugins(self):
        self.pluginNames = self._getPlugins()
        self.plugins = {}
        for module in self.pluginNames:
            mod_name = '%s.%s' % (self.base, module)
            module_tmp = __import__(mod_name, globals(), locals(), [module])
            cls = self._getSubclass(module_tmp, PluginBase)
            self.plugins[module] = cls()

    def _getSubclass(self, module, base_class):
        for name in dir(module):
            obj = getattr(module, name)
            if name == base_class.__name__:
                continue
            try:
                if issubclass(obj, base_class):
                    return obj
            except TypeError:  # If 'obj' is not a class
                pass
        return None

    def _convertToModuleName(self, name):
        return name.replace('.py', '')

    def _getPlugins(self):
        fullPath = os.path.abspath(__file__).split('/')[:-2]
        fullPath = '/'.join(fullPath)
        fullPath = "%s/%s/" % (fullPath, self.base.replace('.', '/'))
        modules = []
        for _, _, modules_tmp in os.walk(fullPath):
            for module in modules_tmp:
                if not module.endswith('.py'):
                    continue
                if module != '__init__.py' and 'Test' not in module:
                    modules.append(self._convertToModuleName(module))
        return modules
