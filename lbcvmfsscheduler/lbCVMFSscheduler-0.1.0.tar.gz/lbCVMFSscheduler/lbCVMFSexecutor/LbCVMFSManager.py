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
import fcntl
import os
import sys
import time

from lbCVMFSscheduler.lbcommons.RabbitMQRPCServer import RPCServer

from LbCVMFSExecuter import Executor
from LbCVMFSLogger import LogCreator
from lbCVMFSscheduler.lbcommons.Messages import RbMessage


class LockManager(object):

    STATUS_SERVER_STATUS = "SERVER-STATUS"

    def __init__(self, LOCKFILE_name, pid, server, logCreator):
        self.LOCKFILE_name = LOCKFILE_name
        self.pid = pid
        self.server = server
        self.STATUS_SERVER_STATUS = "%s-%s" % (self.STATUS_SERVER_STATUS,
                                               self.pid)
        self.logCreator = logCreator
        self.other_is_running = None

    def __enter__(self):
        """
        Try to get the lock file or exit if other process has the lock
        """
        self.lock_file = "%scvmfs_scheduler_lock" % self.LOCKFILE_name
        current_process = None

        self.logCreator.write("Trying to get lock", 0,
                              self.STATUS_SERVER_STATUS)
        # Block other processes in getLock state
        lock_file_descriptor = None
        try:

            lock_file_descriptor = open(self.lock_file, 'a+')

            # temporary lock the file for reading
            fcntl.flock(lock_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file_descriptor.seek(0, 0)
            val = lock_file_descriptor.readline()
            if val != "":
                current_process = val

            if not current_process:
                self.other_is_running = False
            else:
                # look up process if exists
                try:
                    open(os.path.join('/proc', current_process,
                                      'cmdline'), 'rb').read()
                    self.other_is_running = True
                except IOError:  # proc has already terminated
                    self.other_is_running = False
            if not self.other_is_running:
                lock_file_descriptor.seek(0, 0)
                lock_file_descriptor.write("%s" % self.pid)
                lock_file_descriptor.truncate()
            else:
                raise RuntimeError(
                    "Process %s is still running" % current_process)
        except (IOError, RuntimeError) as e:
            # Forcing all the messages on the backup channel
            self.server.forceBackupUse()
            print e
            self.logCreator.write("Fail to get lock", 0,
                                  self.STATUS_SERVER_STATUS)
            self.logCreator.write("Server closing", 0,
                                  self.STATUS_SERVER_STATUS)
            raise
        finally:
            if lock_file_descriptor:
                fcntl.flock(lock_file_descriptor, fcntl.LOCK_UN)
                lock_file_descriptor.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Remove lock
        """
        if self.other_is_running:
            return True
        try:
            os.remove(self.lock_file)
            return True
        except:
            return False


class LbCVMFSManager(object):
    """
    Global manager for cron like jobs on CVMFS
    """
    STATUS_SERVER_INFO = "SERVER-INFO"
    STATUS_SERVER_STATUS = "SERVER-STATUS"

    def __init__(self, dry_run=False, test=False, queueName='commands'):
        """
        Before starting any job, verify if this is the only instance
        running
        """
        self.dry_run = dry_run
        self.test = test
        self.pid = os.getpid()
        self.queueName = queueName
        self.STATUS_SERVER_STATUS = "%s-%s" % (self.STATUS_SERVER_STATUS,
                                               self.pid)
        self.LOGFILE_name = "%s/manager.log" % (
            os.environ.get('LOGDIR', os.environ.get('HOME', ''))
        )
        # Create log first to log starting attempts
        self.server = RPCServer(self.request)
        self.logCreator = LogCreator(self.server, self.LOGFILE_name)

        self.LOCKFILE_name = "%s/var/lock/" % (
            os.environ.get('HOME', '')
        )

        # Create the path to the lock file if it does not exists
        if not os.path.exists(os.path.dirname(self.LOCKFILE_name)):
            os.makedirs(os.path.dirname(self.LOCKFILE_name))

    def interactive(self):
        with LockManager(self.LOCKFILE_name, self.pid, self.server,
                         self.logCreator):
            os.system("/bin/bash --norc")
        self.logCreator.close()

    def start(self):
        self.logCreator.write("Trying to start server", 0,
                              self.STATUS_SERVER_STATUS)

        # Lock the file
        with LockManager(self.LOCKFILE_name, self.pid, self.server,
                         self.logCreator):
            self.logCreator.write("Server starting", 0,
                                  self.STATUS_SERVER_STATUS)
            # Wait for commands
            self.server.setupServer(self.queueName)

        self.logCreator.write("Server closing", 0,
                              self.STATUS_SERVER_STATUS)
        self.logCreator.close()

    def request(self, body):
        """
        Callback for requests
        :param chanel:
        :param method:
        :param props:
        :param body:
        :return:
        """
        message = RbMessage()
        message.updateFromJson(body)
        id = message.getId()

        self.logCreator.write("Running command from client with id: %s" % id,
                              id, self.STATUS_SERVER_INFO)
        payload = message.getPayload()

        # Get the command
        command = payload.get('command', None)
        args = payload.get('args', [])

        # Call the executor
        executor = Executor(command, self.logCreator, args=args, client_id=id,
                            dry_run_mode=self.dry_run, test_mode=self.test)
        try:
            executor.runExecutable()
        except:
            raise
        finally:
            self.logCreator.write("Finished command from client with id: %s" % id,
                                  id, self.STATUS_SERVER_INFO)

            # End the connection
            # time.sleep(0.1)
            # message = RbMessage(id=id)
            # message.setExitMessage()
            # self.server.publish(message.convertToJson())
