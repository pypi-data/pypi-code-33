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
"""
LbInstall specific config for LHCb

:author: Ben Couturier
"""
import os

try:
    import urllib2
except:
    # Python 3 workaround
    from urllib import request as urllib2
import json
import datetime


class Config:

    """ Default configuration for LHCb

    :param defaultRepoURL: a custom default repository url
    :param skipConfig: if true, this flag allows the config
                       to skip the setup of the default
                       configuration.
    """
    def __init__(self, siteroot, defaultRepoURL=None, skipConfig=False,):
        self.CONFIG_VERSION = 1

        repos = {}
        extra_data = {}

        # For the case when we want to override...
        if skipConfig:
            self.repos = repos
            self.exrtrainfo = extra_data
            return

        # Default LHCb URL
        repourl = "http://lhcb-rpm.web.cern.ch/lhcb-rpm/"
        jsonFileUrl = "%srepoinfo.json" % repourl
        localJsonFile = os.path.join(siteroot, "var", "repoinfo.json")
        if defaultRepoURL is not None:
            repourl = defaultRepoURL

        # Now adding the LHCb  URLs
        repos["lhcb"] = {"url": repourl + "/lhcb"}
        repos["lhcb2017"] = {"url": repourl + "/lhcb2017"}
        repos["lhcb2018"] = {"url": repourl + "/lhcb2018"}
        repos["lhcb2019"] = {"url": repourl + "/lhcb2019"}
        repos["lcg"] = {
            "url": "http://lcgpackages.web.cern.ch/lcgpackages/rpms"}
        repos["lhcbext"] = {"url": repourl + "/lcg"}
        repos["lhcbincubator"] = {"url": repourl + "/incubator"}
        repos["lcgbackup"] = {"url": repourl + "/lcgbackup"}

        try:
            response = urllib2.urlopen(jsonFileUrl)
            remote_data = json.loads(response.read())
            local_data = {}
            if os.path.exists(localJsonFile):
                with open(localJsonFile, "r") as f:
                    local_data = json.loads(f.read())
            for repo_name in remote_data.keys():
                if repo_name not in repos.keys():
                    repos[repo_name] = {}
                repos[repo_name]['url'] = remote_data[repo_name]['url']
                extra_data[repo_name] = {
                    'remote_last_update': remote_data[repo_name][
                        'last_update'],
                    'local_last_update': local_data.get(repo_name, {}).get(
                        'last_update', '1970-01-01 00:00:00')
                }
                # overwrite
                local_data[repo_name] = remote_data[repo_name]
            with open(localJsonFile, "w") as f:
                f.write(json.dumps(local_data))
        except Exception as e:
            # Url not ok
            pass

        self.repos = repos
        self.exrtrainfo = extra_data

    def getRepoConfig(self):
        """ return the configuration

        :returns: The repositories configuration map
        """
        return self.repos

    def getRelocateMap(self, siteroot):
        """
        Returns relocate command to be passed to RPM for the repositories

        :param siteroot: the location of the installation area

        :returns: the default relocation map based on the instalation area
        """
        ret = {'/opt/lcg/external': os.path.join(siteroot, 'lcg', 'external'),
               '/opt/lcg': os.path.join(siteroot, 'lcg', 'releases'),
               '/opt/LHCbSoft': siteroot}
        return ret
