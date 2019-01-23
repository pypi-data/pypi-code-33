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

    def perform_task(self, task):
        command = 'manager_gc'
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed")
        