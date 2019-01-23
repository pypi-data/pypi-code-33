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
import threading

from LbCVMFSExecuter import Executor
from LbCVMFSLogger import LogCreator
from LockManager import LockManager
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.CvmfsConDBExchange import CvmfsConDBExchange
from lbmessaging.exchanges.CvmfsProdExchange import CvmfsProdExchange
from lbmessaging.exchanges.Common import get_connection, Message, \
    check_channel, RPCServer, RPCClient
import lbmessaging
import time
from pika import exceptions


from lbCVMFSscheduler import exchangeManager


class LbCVMFSManager(object):
    """
    Global manager for cron like jobs on CVMFS
    """
    STATUS_SERVER_INFO = "SERVER-INFO"
    STATUS_SERVER_STATUS = "SERVER-STATUS"

    SERVER_STOP_COMMAND = "STOP-SERVER"
    SERVER_STOPPED_INFO = "STOPPED-SERVER"
    SERVER_ACK = "STOP-ACK"

    def __init__(self, vhost='/lhcb', exchangeType='CvmfsDevExchange',
                 dry_run=False, test=False, queueName='CronJobs',
                 volumname='lhcbdev.cern.ch', with_gateway=False):
        """
        Before starting any job, verify if this is the only instance
        running
        """
        self.volumname = volumname
        self.vhost = vhost
        self.with_gateway = with_gateway
        self.dry_run = dry_run
        self.test = test
        self.pid = os.getpid()
        self.queueName = queueName
        self.exchangeType = exchangeType

        self.STATUS_SERVER_STATUS = "%s-%s" % (self.STATUS_SERVER_STATUS,
                                               self.pid)
        self.LOGFILE_name = "%s/manager.log" % (
            os.environ.get('LOGDIR', os.environ.get('HOME', ''))
        )
        # Create log first to log starting attempts
        self._connect()

        self.logCreator = LogCreator(self.LOGFILE_name)

        self.LOCKFILE_name = "%s/var/lock/" % (
            os.environ.get('HOME', '')
        )

        # Create the path to the lock file if it does not exists
        if not os.path.exists(os.path.dirname(self.LOCKFILE_name)):
            os.makedirs(os.path.dirname(self.LOCKFILE_name))

    def interactive(self, reason):
        print("You are connected as %s" % os.environ['SUDO_USER'])
        if reason is None:
            print("What is the reason of entering the interactive mode?")
            reason = raw_input()
        print("On the record: %s" % reason)
        self.logCreator.write(
            "Started interactive mode by %s" % os.environ['SUDO_USER'],
            0, self.STATUS_SERVER_INFO)
        self.logCreator.write(
            "Message: %s" % reason,
            0, self.STATUS_SERVER_INFO)
        volname_safe = self.volumname.replace('/', '_').replace('.', '_')
        replay_exchange_name = 'cmvfsstatus.%s' % volname_safe
        server = RPCServer(replay_exchange_name, volname_safe,
                           channel=self.channel,
                           auto_delete=True)
        self.bash_thread = threading.Thread(target=self._start_interactive)
        if LockManager.verify_lock_file(self.LOCKFILE_name):
            self.bash_thread.start()
            return
        print("Please wait for the scheduler to finish the current action...")
        self.broker.send_command(self.SERVER_STOP_COMMAND,
                                 [replay_exchange_name],
                                 priority=lbmessaging.priority(
                                     lbmessaging.EMERGENCY))
        server.receive_and_replay_rpc_message(self._replay_ack,
                                              limit=1)

    def _replay_ack(self, message):
        if message.body[self.SERVER_STOPPED_INFO] == self.volumname:
            self.bash_thread.start()
            return {self.SERVER_ACK: True}
        return {self.SERVER_ACK: False}

    def _start_interactive(self):
        with LockManager(self.LOCKFILE_name, self.pid, force_lock=True):
            # Clear the stop file after getting the lock
            os.system("/bin/bash --norc")
        self.logCreator.write(
            "Ended interactive mode by %s" % os.environ['SUDO_USER'],
            0, self.STATUS_SERVER_INFO)
        self.logCreator.close()

    def _connect(self):
        self.connection = get_connection(vhost=self.vhost)
        self.channel = check_channel(self.connection)
        exchangeType = exchangeManager.get(self.exchangeType,
                                           CvmfsDevExchange)
        self.broker = exchangeType(self.channel)

    def start(self):
        # Lock the file
        with LockManager(self.LOCKFILE_name, self.pid):
            while True:
                if self.channel.is_closed or self.channel.is_closing:
                    self.logCreator.write(
                        "Channel is closed: %s or closing: %s" % (
                            self.channel.is_closed, self.channel.is_closing),
                        0, self.STATUS_SERVER_INFO)
                    while self.channel.is_closing:
                        time.sleep(0.1)
                    self._connect()
                # Wait for commands
                try:
                    message = self.broker.receive_command(self.queueName)
                except exceptions.ConnectionClosed as cc:
                    self.logCreator.write(
                        "Channel is closed when getting the message",
                        0, self.STATUS_SERVER_INFO)
                    self._connect()
                    try:
                        message = self.broker.receive_command(self.queueName)
                    except:
                        self.logCreator.write(
                            "Error in getting the message",
                            0, self.STATUS_SERVER_INFO)
                self.logCreator.write(
                    "Got message",
                    0, self.STATUS_SERVER_INFO)
                if message is None:
                    self.logCreator.write(
                        "Message is None",
                        0, self.STATUS_SERVER_INFO)
                    # Strange behaviour after a long installation
                    self._connect()
                    message = self.broker.receive_command(self.queueName)
                    if message is None:
                        self.logCreator.write(
                            "Second message is None, Exit",
                            0, self.STATUS_SERVER_INFO)
                        break
                try:
                    if message.body.command == self.SERVER_STOP_COMMAND:
                        exchange = message.body.arguments[0]
                        volname_safe = self.volumname.replace(
                            '/', '_').replace('.', '_')
                        client = RPCClient(exchange,
                                           routing_keys=None,
                                           auto_delete=True,
                                           channel=self.channel)

                        def wrapper(message):
                            if message.body[self.SERVER_ACK] is True:
                                return True
                            return False

                        client.send_and_receive_rpc_message(
                            volname_safe,
                            {self.SERVER_STOPPED_INFO: self.volumname},
                            wrapper, limit=1)
                        break
                    meta = None
                    if '--with_meta' in message.body.arguments:
                        meta = {
                            'method_frame': message.method_frame,
                            'header_frame': message.header_frame
                        }
                    res = self.request(message.body, meta=meta)
                except:
                    self.broker.handle_processing_error(message)
        self.logCreator.close()

    def request(self, body, meta=None):
        """
        Callback for requests
        :param chanel:
        :param method:
        :param props:
        :param body:
        :return:
        """

        # Get the command
        command = body.command
        args = [str(x) for x in body.arguments]
        id = command

        # Call the executor
        executor = Executor(command, self.volumname, self.with_gateway,
                            self.logCreator, args=args, client_id=id,
                            dry_run_mode=self.dry_run, test_mode=self.test,
                            meta=meta)
        try:
            executor.runExecutable()
        except Exception as e:
            self.logCreator.write(
                "Error in command from client with id: %s - %s" % (id, str(e)),
                id, self.STATUS_SERVER_INFO)
            raise
        finally:
            self.logCreator.write(
                "Finished command from client with id: %s" % id,
                id, self.STATUS_SERVER_INFO)
