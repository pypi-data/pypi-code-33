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
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''
import os
import subprocess
from lbCVMFSscheduler.lbCVMFSexecutor.LbCVMFSStats import CVMFSStats
from random import randint
from time import sleep


class Executor:
    """
    Execute a cron job command
    """

    STATUS_RUNNING = 'RUNNING'
    STATUS_FAIL = 'FAILED'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_STARTED = 'STARTED'

    def __init__(self, execName,  volumename, with_gateway=False,
                 logger=None, args=[], client_id=None,
                 dry_run_mode=False, test_mode=False,
                 meta=None):
        if not logger:
            raise Exception("Error: logger not found")
        self.dry_run_mode = dry_run_mode
        self.test_mode = test_mode
        self.client_id = client_id
        self.BINFOLDER = "%s/bin/" % os.environ.get("HOME", '')
        self.name = "%s%s" % (self.BINFOLDER, execName)
        self.args = args
        self.logger = logger
        self.priority = None
        self.max_retry = None
        if meta:
            self.priority = meta['header_frame'].priority
            self.max_retry = meta['header_frame'].headers.get('max_retry', 3)
            self.args.append('--MPriority=%s' % self.priority)
            self.args.append('--MMaxRetry=%s' % self.max_retry)
        self.stat_output = 'cvmfs_stats.dat'
        self.stats = CVMFSStats(volumename, with_gateway=with_gateway,
                                logger=self.logger,
                                log_filename=self.stat_output)

    def checkExecutable(self):
        """
        Verifies if the executable is on disk
        :return:
        """
        if not os.path.exists(self.name):
            self.logger.write(
                "Executable %s not found! Job ended with code: 1" % self.name,
                self.client_id, self.STATUS_FAIL)
            sleep(0.1)
            raise Exception("Executable %s not found!" % self.name)
        # self.logger.write("Found execute %s" % self.name, self.client_id,
        #                   self.STATUS_STARTED)

    def runExecutable(self):
        """
        Runs the executable
        :return:
        """
        # self.logger.write("Trying to execute %s" % self.name, self.client_id,
        #                   self.STATUS_STARTED)
        self.checkExecutable()
        command = [self.name]
        command.extend(self.args)

        self.logger.write("Starting execute %s" % ' '.join(command),
                          self.client_id,
                          self.STATUS_STARTED)
        if not self.dry_run_mode:
            proc = subprocess.Popen(command, shell=False, bufsize=1,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            while (True):
                line = proc.stdout.readline()
                line = line.decode()
                if line == "":
                    break
                self.logger.write(line, self.client_id, self.STATUS_RUNNING)

            # Check status
            proc.wait()
            rc = proc.returncode
        else:
            self.logger.write("In dry run mode",
                              self.client_id,
                              self.STATUS_STARTED)
            rc = 0
            if self.test_mode:
                time_sleep = randint(10, 15 * 60)
                self.logger.write("Sleeping for %s" % time_sleep,
                                  self.client_id,
                                  self.STATUS_STARTED)
                sleep(time_sleep)
        if rc == 0:
            status = self.STATUS_SUCCESS
        else:
            status = self.STATUS_FAIL
        self.logger.write('Job ended with code: %s' % rc,
                          self.client_id,
                          status)
        try:
            self.stats.run()
        except:
            pass
