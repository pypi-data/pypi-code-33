###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module that manages the DEV install area on /cvmfs/lhcbdev.cern.ch/lib

@author: Ben Couturier & Stefan-Gabriel CHITIC
'''
import os
import logging
import yaml
from pykwalify.core import Core
from pykwalify.errors import SchemaError
import re


class YamlManager:

    def __init__(self, configFile):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)
        self.configfile = configFile
        if not os.path.exists(self.configfile):
            raise Exception("Could not find config file %s" %
                            self.configfile)

    def loadConfig(self):
        ''' Just load the YAML config file '''
        with open(self.configfile) as f:
            config = yaml.load(f)
            return config

    def getPrefixList(self):
        ''' Get the list of LCG packages to install '''
        config = self.loadConfig()
        prefixlist = []
        for p in config["packages"]:
            name = p["name"]
            for lcg in p["LCG"]:
                exclusions = []
                for x in config['exclusions']:
                    if x['LCG'] == lcg:
                        exclusions.extend([re.compile(reg)
                                           for reg in x['regex']])
                for v in p["versions"]:
                    prefix = "LCG_%s_%s_%s" % (lcg, name, v)
                    self.log.info("Looking for %s" % prefix)
                    prefixlist.append({
                        'prefix': prefix,
                        'exclusions': exclusions
                    })
        return prefixlist

    def validateYAML(self):
        ''' Validates the yaml config file against the used schema '''
        script_dir = os.path.dirname(os.path.realpath(__file__))
        schema_file = os.path.join(script_dir, 'schema.yaml')
        self.log.warning("Using schema file %s" % schema_file)
        c = Core(source_file=self.configfile, schema_files=[schema_file])
        try:
            c.validate(raise_exception=True)
            return True
        except SchemaError as e:
            self.log.error("There was a problem validating with the file %s:"
                           "%s" % (self.configfile, str(e)))
            return False
