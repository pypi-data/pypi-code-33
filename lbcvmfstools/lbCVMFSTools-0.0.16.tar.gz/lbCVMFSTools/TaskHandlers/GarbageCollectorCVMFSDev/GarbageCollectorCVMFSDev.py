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
@author: Stefan-Gabriel CHITIC, Ben Couturier
'''
import logging
import subprocess
import os
import sys
from lbCVMFSTools.Injector import inject
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
import subprocess

FREQ = 24 * 60 * 60

class GarbageCollectorCVMFSDev(TaskHandlerInterface, object):

    def __init__(self, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(GarbageCollectorCVMFSDev, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''

    def get_list_of_tasks(self):
        return ['manager_gc']

    def _execute_command(self, command):
        home = os.environ['HOME']
        command = os.path.join(home, 'bin', command)
        command = command.split(' ')
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed:\nError code:%s\nOutput:%s\nError:%s" % (command, retCode, out, err))

    def perform_task(self, task):
        # install the slots
        logging.info("Manager_gc starting")
        try:
            self._execute_command("stratum0stats.py >> ${LOGDIR}/cvmfs_stats.dat")
            self._execute_command("checkRemove >> ${LOGDIR}/manager.log")
            self._execute_command("stratum0stats.py >> ${LOGDIR}/cvmfs_stats.dat")
            self._execute_command("cvmfs_server gc -t '3 days ago' -f lhcbdev.cern.ch >> ${LOGDIR}/manager.log")
            loggin.info("CVMFS gc done")
            self._execute_command("stratum0stats.py >> ${LOGDIR}/cvmfs_stats.dat")
        except Exception as e:
            raise e
        