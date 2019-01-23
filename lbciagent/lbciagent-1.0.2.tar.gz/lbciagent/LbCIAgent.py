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
from lbciagent.Override import adminOverride
from datetime import datetime
import threading
import signal


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
        # Setup enviroment
        self.vhost = vhost
        self.consumers = {}
        self.threads = []
        self.running = False
        signal.signal(signal.SIGINT, self.signalHandler)
        signal.signal(signal.SIGTERM, self.signalHandler)

    def signalHandler(self, signal=None, stack=None):
        self.logger.warn("Closing agent")
        self.running = False
        for handler in self.consumers.keys():
            channel = self.consumers[handler]['channel']
            channel.stop_consuming()

    def start(self):
        self.running = True
        t = threading.Thread(
            target=self._start_listenting,
            args=('consume_build_ready',
                  self.convertBuildReadyMessages,
                  self.build_ready_queue))
        self.threads.append(t)
        t = threading.Thread(
            target=self._start_listenting,
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

    def _start_listenting(self, method, convertor, queue):
        channel = check_channel(get_connection(vhost=self.vhost))
        command_broker = CvmfsDevExchange(channel)
        self.consumers[convertor.__name__] = {
            'broker': command_broker,
            'channel': channel
        }
        with channel:
            broker = ContinuousIntegrationExchange(channel)
            method = getattr(broker, method)
            method(convertor, queue)

    def convertEnvKitMessages(self, full_message):
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
        command_broker = self.consumers['convertBuildReadyMessages']['broker']
        message = full_message.body
        message_with_priority = self.getSystemPriority(message)
        if not message_with_priority:
            self.logger.warn('%s-%s-%s-%s-P:%s-D:%s DISCARDED' % (
                message.slot, message.build_id, message.platform,
                message.project, message.priority, message.deployment))
            return True
        # Override
        message_override = adminOverride(message_with_priority)
        if message_override != message_with_priority:
            self.logger.warn('%s-%s-%s-%s-P:%s-D:%s OVERRIDE' % (
                message_with_priority.slot,
                message_with_priority.build_id,
                message_with_priority.platform,
                message_with_priority.project,
                message_with_priority.priority,
                message_with_priority.deployment))
        command = 'installNightlies'
        args = [message_override.slot, message_override.build_id,
                message_override.platform, message_override.project]
        now = datetime.now()
        expiration = (now.replace(hour=23, minute=59,
                                  second=59) - now).total_seconds()
        expiration = int(expiration * 1000)
        command_broker.send_command(command, args,
                                    expiration=expiration,
                                    priority=message_override.priority)
        self.logger.warn('%s-%s-%s-%s-P:%s-D:%s CONVERTED' % (
            message_override.slot,
            message_override.build_id,
            message_override.platform,
            message_override.project,
            message_override.priority,
            message_override.deployment))
        return True

    def getSystemPriority(self, message):
        slots_to_install = self._getSlots()
        if message.deployment is None:
            return None
        if message and 'cvmfs' not in [x.lower() for x in message.deployment]:
            return None
        try:
            slot_position = slots_to_install.index(message.slot)
        except:
            slot_position = len(slots_to_install)
        len_positions = len(slots_to_install)
        raw_priority = (len_positions - slot_position) * 1.0 / len_positions
        priority = lbmessaging.priority(lbmessaging.LOW, raw_priority)
        message_tmp = message._asdict()
        message_tmp['priority'] = priority
        return PhysBuildReadyMessage(**message_tmp)

    def _getSlots(self):
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
