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
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''
import os
import re
import sys
import logging
import time

import lbmessaging
from lbmessaging.exchanges.Common import get_connection, \
    InterruptedProcessing, check_channel
from lbmessaging.exchanges.ContinuousIntegrationExchange import \
    ContinuousIntegrationExchange, PhysBuildReadyMessage, EnvkitReadyMessage
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from datetime import datetime
import threading
import signal


priority_platforms = {
    'lhcb-head': 'x86_64-centos7-gcc7-opt',
    'lhcb-sim09': 'x86_64-slc6-gcc49-opt',
    'lhcb-2018-patches': 'x86_64-centos7-gcc7-opt',
    'lhcb-gaudi-head': 'x86_64-centos7-gcc7-opt',
    'lhcb-tdr-test': 'x86_64-centos7-gcc7-opt',
    'lhcb-run2-patches': 'x86_64-centos7-gcc7-opt',
    'lhcb-gauss-dev': 'x86_64-centos7-gcc7-opt',
    'lhcb-sim09-upgrade': 'x86_64-slc6-gcc49-opt',
    'lhcb-2017-patches': 'x86_64-centos7-gcc62-opt',
    'lhcb-2016-patches': 'x86_64-slc6-gcc49-opt',
    'lhcb-lcg-dev3': 'x86_64-centos7-gcc7-opt',
    'lhcb-lcg-dev4': 'x86_64-centos7-gcc7-opt',
    'lhcb-gauss-newgen': 'x86_64-slc6-gcc49-opt',
    'lhcb-clang-test': 'x86_64-centos7-clang50-opt',
    'lhcb-reco14-patches': 'x86_64-slc5-gcc46-opt',
    'lhcb-stripping21-patches': 'x86_64-slc6-gcc48-opt',
    'lhcb-stripping24-patches': 'x86_64-slc6-gcc49-opt'
}


def isPriorityPlatform(slot, platform):
    return priority_platforms.get(slot, 'None') == platform


def computePriority(slot, platform):
    """
    Computes the priority of a slot / platform
    :return: the lbmessaging normalized priority
    """
    slots_to_install = _getSlots()

    # Compute slot priority
    try:
        slot_position = slots_to_install.index(slot)
    except:
        slot_position = len(slots_to_install)
    len_positions = len(slots_to_install)

    # Normalized priority of the whole slot, taking into account its
    # position in the list
    slot_priority = (len_positions - slot_position) * 1.0 / len_positions

    # If the platform has high priority, to ensure that it gets i
    # nstalled straight away,
    # we force the prio to be in [0.5, 1]
    # Otherwise the priority is half teh slot_priority (therefore in [0, 0.5]
    priority = slot_priority / 2.0
    if isPriorityPlatform(slot, platform):
        priority += 0.5
    return lbmessaging.priority(lbmessaging.LOW, priority)


def _getSlots():
    """ Util function to get slots of interest from conf file """
    slotfile = os.path.join(os.environ.get("HOME"), "slotsOnCVMFS.txt")

    slots = []
    with open(slotfile) as f:
        for l in f.readlines():
            if re.match("^\s*#", l):
                continue
            else:
                slots.append(l.rstrip())
    return slots


class LbCIAgent(object):
    """
    Global manager for cron like jobs on CVMFS
    """

    def __init__(self, vhost='/lhcb'):
        """
        Before starting any job, verify if this is the only instance
        running
        """

        self.pid = os.getpid()
        self.build_ready_queue = 'BuildReadyCIAgent'
        self.env_ready_queue = 'EnvKitReadyCIAgent'
        logging.basicConfig(stream=sys.stderr)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.WARNING)

        # Create log first to log starting attempts
        # Setup environment
        self.vhost = vhost
        self.consumers = {}
        self.threads = []
        self.running = False
        signal.signal(signal.SIGINT, self.signalHandler)
        signal.signal(signal.SIGTERM, self.signalHandler)

    def signalHandler(self, signal=None, stack=None):
        """
        Signals the agent closing
        """
        self.logger.warn("Closing agent")
        self.running = False
        for handler in self.consumers.keys():
            channel = self.consumers[handler]['channel']
            channel.stop_consuming()

    def start(self):
        """
        Starts consuming messages for both build ready and envkit ready
        """
        self.running = True
        t = threading.Thread(
            target=self._start_listening,
            args=('consume_build_ready',
                  self.convertBuildReadyMessages,
                  self.build_ready_queue))
        self.threads.append(t)
        t = threading.Thread(
            target=self._start_listening,
            args=('consume_envkit_ready',
                  self.convertEnvKitMessages,
                  self.env_ready_queue))
        self.threads.append(t)
        for t in self.threads:
            t.start()
        while(self.running):
            time.sleep(1)
        for t in self.threads:
            t.join()
        self.logger.warn("Agent closed")

    def _start_listening(self, method, converter, queue):
        """
        Start listening (consuming) messages and converting them to CVMFS
        commands
        :param method: the consuming method name in the
                       ContinuousIntegrationExchange
        :param converter: the conversion functions
        :param queue: the listening (consuming) queue
        :return:
        """
        channel = check_channel(get_connection(vhost=self.vhost))
        command_broker = CvmfsDevExchange(channel)
        self.consumers[converter.__name__] = {
            'broker': command_broker,
            'channel': channel
        }
        with channel:
            broker = ContinuousIntegrationExchange(channel)
            method = getattr(broker, method)
            method(converter, queue)

    def convertEnvKitMessages(self, full_message):
        """
        Function that converts a env kit ready message to CVMFS command message
        :param full_message: the original EnvkitReadyMessage message
        :return: the converted message
        """
        command_broker = self.consumers['convertEnvKitMessages']['broker']
        message = full_message.body
        command = 'env_kit_installer'

        args = [message.flavour, message.platform,
                message.version, message.url]
        priority = lbmessaging.priority(lbmessaging.NORMAL, 1.0)
        command_broker.send_command(command, args,
                                    priority=priority)
        self.logger.warn('%s-%s-%s CONVERTED' % (
            message.flavour,
            message.platform,
            message.version))
        return True

    def convertBuildReadyMessages(self, full_message):
        """
        Function that converts a build ready message to CVMFS command message
        :param full_message: the original PhysBuildReadyMessage message
        :return: the converted message
        """
        command_broker = self.consumers['convertBuildReadyMessages']['broker']
        message = full_message.body
        message_with_priority = self.filterAndSetPriority(message)
        if not message_with_priority:
            self.logger.warn('%s-%s-%s-%s-P:%s-D:%s DISCARDED' % (
                message.slot, message.build_id, message.platform,
                message.project, message.priority, message.deployment))
            return True

        command = 'installNightlies'
        args = [message_with_priority.slot, message_with_priority.build_id,
                message_with_priority.platform, message_with_priority.project]
        now = datetime.now()
        expiration = (now.replace(hour=23, minute=59,
                                  second=59) - now).total_seconds()
        expiration = int(expiration * 1000)
        command_broker.send_command(
            command, args, expiration=expiration,
            priority=int(message_with_priority.priority))
        self.logger.warn('%s-%s-%s-%s-P:%s-D:%s CONVERTED' % (
            message_with_priority.slot,
            message_with_priority.build_id,
            message_with_priority.platform,
            message_with_priority.project,
            message_with_priority.priority,
            message_with_priority.deployment))
        return True

    def filterAndSetPriority(self, message):
        """
        Computes the priority of the message based on slotsOnCVMFS.txt (from
        home dir)
        :param message: the message without priority
        :return: the message with the priority if the message is for CVMFS
                installation or None otherwise.
        """
        if message.deployment is None:
            return None
        if message and 'cvmfs' not in [x.lower() for x in message.deployment]:
            return None

        message_tmp = message._asdict()
        message_tmp['priority'] = computePriority(message.slot,
                                                  message.platform)
        return PhysBuildReadyMessage(**message_tmp)


