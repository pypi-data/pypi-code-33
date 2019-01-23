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
import signal
import logging

import lbmessaging
from lbmessaging.Common import get_connection, InterruptedProcessing
from lbmessaging.ContinuousIntegrationExchange import \
    ContinuousIntegrationExchange, ContinuousIntegrationMessage
from lbmessaging.CvmfsDevExchange import CvmfsDevExchange
from lbciagent.Override import adminOverride


def signalHandler(signal=None, stack=None):
    raise InterruptedProcessing


signal.signal(signal.SIGINT, signalHandler)
signal.signal(signal.SIGTERM, signalHandler)


class LbCIAgent(object):
    """
    Global manager for cron like jobs on CVMFS
    """

    def __init__(self, build_queue_name='BuildReadyCIAgent', connection=None):
        """
        Before starting any job, verify if this is the only instance
        running
        """

        self.pid = os.getpid()
        self.build_queue_name = build_queue_name
        logging.basicConfig(stream=sys.stderr)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.WARNING)

        # Create log first to log starting attempts
        # Setup enviroment
        if connection:
            self._connection = connection
        else:
            self._connection = get_connection(vhost='/lhcb')

    def start(self):
        with self._connection:
            self.build_ready_broker = ContinuousIntegrationExchange(
                self._connection)
            self.command_broker = CvmfsDevExchange(self._connection)
            # get the list of builds
            self.build_ready_broker.consume_build_ready(self.convertMessages,
                                                        self.build_queue_name)

    def convertMessages(self, full_message):
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
        self.command_broker.send_command(command, args,
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
        return ContinuousIntegrationMessage(**message_tmp)

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
