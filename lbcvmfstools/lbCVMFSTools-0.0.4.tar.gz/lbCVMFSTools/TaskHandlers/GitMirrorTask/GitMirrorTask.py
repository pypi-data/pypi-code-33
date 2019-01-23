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
CVMFS nightlies installer
@author: Stefan-Gabriel CHITIC
'''
import logging
import subprocess
import os
import hashlib

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface


class GitMirrorTask(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True,
                 repodir='/cvmfs/lhcbdev-test.cern.ch/git-mirrors',
                 *args, **kwargs):
        super(GitMirrorTask, self).__init__(*args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.repoDir = repodir
        logging.getLogger().setLevel(logging.INFO)

    def _md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_list_of_tasks(self):
        allrepos = os.listdir(self.repoDir)
        todo = []
        for r in allrepos:
            path = os.path.join(self.repoDir, r)
            path_head = os.path.join(path, 'FETCH_HEAD')
            md5 = self._md5(path_head)
            todo.append({
                'path': path,
                'md5': md5
            })
        return [todo]

    def perform_task(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        # BY default we consider all is there
        needPublish = False
        # Now installing and checking the difference
        for task in tasks:
            repo = task['path']
            try:
                logging.info("%sUpdating git repo: %s" % (self.log_prefix,
                                                          repo))
                subprocess.call(
                    ["git", "--git-dir=%s" % repo, "remote", "update",
                     "--prune"])
                path_head = os.path.join(repo, 'FETCH_HEAD')
                md5 = self._md5(path_head)
                if md5 != task['md5']:
                    logging.info("%sGit repo %s has changed" % (self.log_prefix,
                                                               repo))
                    needPublish = True
            except Exception as e:
                logging.info(
                    "%Git update problem. Ignoring to avoid transaction"
                    "rollback" % self.log_prefix)
                pass

        if not needPublish and self.installOnCvmfs:
            logging.info(
                "%sNo new files to install - aborting transaction" %
                self.log_prefix)
            raise Exception("No new files, aborting transaction")
