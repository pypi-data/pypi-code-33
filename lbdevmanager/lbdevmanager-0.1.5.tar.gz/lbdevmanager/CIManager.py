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

@author: Ben Couturier
'''

import logging
from lbdevmanager.YamlManager import YamlManager
from lbdevmanager.GitManager import GitManager
from lbdevmanager.LbInstallManager import LbInstallManager


class CIManager:

    def __init__(self, siteroot=None, conffile=None,
                 repo=None, token=None, username=None,
                 branch=None, vhost='/lhcb'):
        """

        :param siteroot: the installation area for LbInstall
        :param conffile: the yaml file we are interested in processing
        :param repo: the name of the git repository where the yaml file
                     is stored
        :param token: the gitlab token used to login into gitlab.(Used if
                      the machine that runs the scripts has not been ssh paired)
        :param username: the gitlab user used to login into gitlab (Used if
                         the machine that runs the scripts has not been ssh
                         paired)
        :param branch: the name of the branch used to store the list of files
                       to install. The default value is installed_files
        :param tag: the name of the tag used to mark the already installed files
                    The default value is lastinstalled
        """
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)
        self.installerManager = None
        self.yamlManager = None
        self.gitManager = None
        if conffile:
            self.yamlManager = YamlManager(conffile)
        if siteroot:
            self.installerManager = LbInstallManager(siteroot)
        if repo:
            self.gitManager = GitManager(repo=repo,
                                         token=token,
                                         branch=branch,
                                         username=username,
                                         vhost=vhost)

    def validateYAML(self):
        ''' Validates the yaml config file against the used schema '''
        if self.yamlManager:
            return self.yamlManager.validateYAML()
        raise Exception("YAML file not present")

    def check(self):
        ''' Check what should be installed... '''
        if self.yamlManager:
            # First looking up the list of required packages
            prefixlist = self.yamlManager.getPrefixList()
        else:
            raise Exception("YAML file not present")
        if self.gitManager and self.installerManager:
            return self.gitManager.UpdateListOfFilesToInstall(
                prefixlist, self.installerManager)
        else:
            raise Exception("Git manager or lb install manager params problem")
