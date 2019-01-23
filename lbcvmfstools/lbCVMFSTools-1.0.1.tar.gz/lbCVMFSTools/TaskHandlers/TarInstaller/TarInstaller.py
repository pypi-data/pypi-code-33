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
Tar installer
@author: Stefan-Gabriel CHITIC
'''
import logging
import os
import urllib2
import tempfile
import subprocess

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface

FREQ = 0


class TarInstaller(TaskHandlerInterface, object):

    def __init__(self, url, root, prefix, installOnCvmfs=True,
                 repodir='/cvmfs/lhcb.cern.ch/lib/lhcb/git-conddb',
                 *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(TarInstaller, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        self.url = url
        self.root = root
        self.prefix = prefix
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.repoDir = repodir
        logging.getLogger().setLevel(logging.INFO)

    def get_list_of_tasks(self):
        return [{
            'url': self.url,
            'root': self.root,
            'prefix': self.prefix,
        }]

    def _comnunicate(self, command):
        command = command.split(' ')
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed")
        return out

    def perform_task(self, tasks):
        # Download the url
        url = tasks['url']
        dirpath = tempfile.mkdtemp()
        file_name = os.path.join(dirpath, url.split('/')[-1])
        logging.info("Downloading %s to %s" % (url, file_name))
        u = urllib2.urlopen(url)
        with open(file_name, 'wb') as f:
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
        # Remove old path
        remove_path = os.path.join(tasks['root'], tasks['prefix'])
        if os.path.exists(remove_path):
            res = self._comnunicate(
                "rm -rf %s" % (remove_path)) == ''
            logging.info("Removing path %s results: %s" % (remove_path, res))
        # Extract the url
        res = self._comnunicate(
            "tar -x -j --directory=%s -f %s" % (tasks['root'], file_name))
        if res == '':
            logging.info("Successfully extracted %s to %s" % (file_name,
                                                              tasks['root']))
        else:
            raise Exception("Failed extracting %s to %s" % (file_name,
                                                            tasks['root']))
