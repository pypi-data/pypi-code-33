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
import logging
from lbCVMFSchecker.PluginManager import LbPluginManager


if __name__ == '__main__':
    logging.basicConfig(format="[%(asctime)s] "
                               "%(levelname)-8s:"
                               "%(message)s")
    logging.getLogger().setLevel(logging.INFO)

    l = LbPluginManager()
    l.executeAll()
