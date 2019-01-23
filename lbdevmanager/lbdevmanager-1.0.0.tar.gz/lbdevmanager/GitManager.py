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
from git import Repo
import tempfile
from datetime import datetime
from lbdevmanager.YamlManager import YamlManager
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.Common import get_connection
import lbmessaging
import re


class GitManager:

    GITLAB_URL = 'https://%s:%s@gitlab.cern.ch'
    GITLAB_BRANCH = 'install_files'
    GITLAB_TAG = 'requested'
    GITLAB_MASTER_TAG = 'last_installed'

    def __init__(self, repo_path=None,
                 vhost='/lhcb',
                 repo=None, token=None, username=None,
                 branch=None, tag=None, master_tag=None):
        """

        :param repo_path: the path to an aready cloned git repo
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
        self.output_file = None
        if branch:
            self.GITLAB_BRANCH = branch
        if tag:
            self.GITLAB_TAG = tag
        if master_tag:
            self.GITLAB_MASTER_TAG = master_tag
        self.repo = repo
        self.token = token
        self.username = username
        self.repo_path_cvmfs = None
        connection = get_connection(vhost=vhost)
        self.broker = CvmfsDevExchange(connection)
        self.priority = lbmessaging.priority(lbmessaging.NORMAL)

        if repo_path:
            self.repo_path_cvmfs = repo_path
            self._createRepoFromCloned(repo_path)
        elif self.repo:
            # Repo sanity check
            if self.repo[0] == '/':
                self.repo = self.repo[1:]
            self.url = self.GITLAB_URL % (self.username, self.token)
            self.url = "%s/%s" % (self.url, self.repo)
            self._cloneRepo()
        self._changeToTechnicalBranch()

    def _createRepoFromCloned(self, path):
        self.target_dirpath = path
        self.cloned_repo = Repo(path)

    def _cloneRepo(self):
        if self.repo and (self.token and self.username):
            self.target_dirpath = tempfile.mkdtemp()
            # Clone
            self.cloned_repo = Repo.clone_from(self.url, self.target_dirpath)
            return
        raise Exception("Can't clone the repo %s " % self.url)

    def _changeToTechnicalBranch(self):
        if self.cloned_repo.active_branch.name != self.GITLAB_BRANCH:
            try:
                self.cloned_repo.git.checkout(self.GITLAB_BRANCH)
            except:
                # Creating branch
                self.cloned_repo.git.checkout('master', b=self.GITLAB_BRANCH)
        self.cloned_repo.git.pull('origin', self.GITLAB_BRANCH)
        # Add the list to cloned
        if not os.path.exists("%s/var/" % self.target_dirpath):
            os.makedirs("%s/var/" % self.target_dirpath)
        self.list_path = "%s/%s" % (self.target_dirpath, 'var/toInstall.list')

    def GetInstalledPkg(self):
        already_there = []
        if os.path.exists(self.list_path):
            with open(self.list_path, 'r') as f:
                for r in f.readlines():
                    already_there.append(r.replace('\n', ''))
        return already_there

    def GetYamlContent(self):
        if self.cloned_repo.active_branch.name != 'master':
            self.cloned_repo.git.checkout('master')
        yaml_path = "%s/%s" % (self.target_dirpath, 'lcg-packages.yaml')
        yaml_manager = YamlManager(yaml_path)
        self._changeToTechnicalBranch()
        return yaml_manager.getPrefixList()

    def RemoveFromListOfFiles(self, rpmlist):
        self._changeToTechnicalBranch()
        already_there = self.GetInstalledPkg()
        with open(self.list_path, 'w') as f:
            for r in already_there:
                if r in rpmlist:
                    continue
                f.write(r)
                f.write('\n')
        f.close()
        date_row = datetime.now().strftime('%Y-%m-%d %H:%M:%S ')
        comment = "Removed files @ %s" % date_row
        commitID = self._commitFile(self.list_path, comment,
                                    self.GITLAB_BRANCH)

    def _isPrefixInList(self, prefix, seen_list):
        for el in seen_list:
            if el.startswith(prefix):
                return True
        return False

    def _commitFile(self, filename, comment, branch):
        # Add the file to commit
        self.cloned_repo.git.add("%s" % filename)
        id = None
        try:
            commit = self.cloned_repo.git.commit(m=comment)
            pattern = '\[install_files (.*)\] (.*)'
            id = re.match(pattern, commit).group(1)
            # Push
            self.cloned_repo.git.push('origin', '%s:%s' % (branch, branch))
        except Exception as e:
            # Nothing to do
            self.log.error(e)
            pass
        return id

    def _getTagRef(self):
        # Get the diff from last run
        tags = self.cloned_repo.tags
        self.tag_ref = None
        for tag in tags:
            if str(tag) == self.GITLAB_TAG:
                self.tag_ref = tag

    def UpdateListOfFilesToInstall(self, prefixlist,
                                   lbinstallManager):
        ''' Check what should be installed... '''
        self.log.warning("There are %d packages to install:" % len(prefixlist))
        # Now proceeding to the installation
        missing_results = []
        if (len(prefixlist) > 0):
            # Check if the file hasn't been install in the past and if not,
            # append it
            rpmlist = []
            already_there = self.GetInstalledPkg()
            for prefixWithExclusions in prefixlist:
                prefix = prefixWithExclusions['prefix']
                if self._isPrefixInList(prefix, already_there):
                    continue
                prefixWithExclusions['prefix'] = prefix.replace('+', '\+')
                pkglist = lbinstallManager.checkPackagesInRemoteDatabase(
                    prefixWithExclusions)
                if len(pkglist) == 0:
                    missing_results.append((prefix))
                for p in pkglist:
                    rpmlist.append(p.rpmName())
            to_install = []
            with open(self.list_path, 'a') as f:
                for r in rpmlist:
                    if r in already_there:
                        continue
                    to_install.append(r)
                    f.write(r)
                    f.write('\n')
            # Commit the file
            date_row = datetime.now().strftime('%Y-%m-%d %H:%M:%S ')
            comment = "Update files to install @ %s" % date_row
            commitID = self._commitFile(self.list_path, comment,
                                        self.GITLAB_BRANCH)
            # Send list to RabbitMQ
            args = ['--toinstall="%s"' % ' '.join(to_install),
                    '--commitID=%s' % commitID,  '--with_meta']
            self.broker.send_command('manager_dev',
                                     args,
                                     priority=self.priority)

        return missing_results

    def GetFilesDiffToInstall(self):
        # Get the diff from last run
        self._getTagRef()
        rpm_names = []
        if not self.tag_ref:
            with open(self.list_path, 'r') as f:
                for r in f.readlines():
                    rpm_names.append(r.replace('\n', ''))
        else:
            self.log.debug("Comparing to tag")
            tag_commit = self.tag_ref.commit
            # Iterate the last commits since tag
            commit = self.cloned_repo.head.commit
            list_path = self.list_path
            if self.repo_path_cvmfs:
                list_path = list_path.replace(self.repo_path_cvmfs, '.')
            diffs = self.cloned_repo.git.diff(
                tag_commit, commit, list_path).split('\n')
            for diff in diffs[4:]:
                if '@@' in diff:
                    diff = diff.split('@@')[-1]
                if len(diff) == 0:
                    continue
                if diff[0] == '+':
                    rpm_names.append(diff[1:].strip().replace('\\\\', '\\'))
        return rpm_names

    def UpdateTags(self):
        self._getTagRef()
        # Remove old tag
        if self.tag_ref:
            self.cloned_repo.delete_tag(self.GITLAB_TAG)
            self.cloned_repo.delete_tag(self.GITLAB_MASTER_TAG)
            self.cloned_repo.git.push('origin', ':refs/tags/%s' %
                                      self.GITLAB_TAG)
            self.cloned_repo.git.push('origin', ':refs/tags/%s' %
                                      self.GITLAB_MASTER_TAG)
        # Create tag
        self.cloned_repo.git.pull('origin', 'master')
        self.cloned_repo.git.push('origin',
                                  '%s:%s' % (self.GITLAB_BRANCH,
                                             self.GITLAB_BRANCH))
        self.cloned_repo.create_tag(self.GITLAB_TAG, self.GITLAB_BRANCH)
        self.cloned_repo.create_tag(self.GITLAB_MASTER_TAG, 'master')

        # Push
        self.cloned_repo.git.push('--tags')
