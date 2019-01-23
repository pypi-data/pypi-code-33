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
import json
import uuid


class RbMessage(object):
    '''
    Generic Class for RabbitMQ messages
    '''

    def __init__(self, id=None, payload={}):
        self.id = id
        self.payload = payload
        if self.id is None:
            self.id = str(uuid.uuid4())

    def updateFromJson(self, json_msg):
        """
        Updates a message from queue message
        :param json: the message from queue
        """
        tmp = json.loads(json_msg)
        try:
            self.id = tmp['id']
            self.payload = tmp['payload']
        except:
            raise Exception("Message cannot be converted")

    def setExitMessage(self):
        self.payload['exit'] = '1'

    def setPayload(self, payload):
        """
        Sets the message payload
        :param payload: the data to be set
        """
        self.payload = payload

    def setPayloadFromJson(self, json):
        """
        Sets the message payload from json format
        :param json: the data to be set
        """
        self.setPayload(json.loads(json))

    def getId(self):
        """
        Gets the message payload
        :return: the message payload
        """
        return self.id

    def getPayload(self):
        """
        Gets the message payload
        :return: the message payload
        """
        return self.payload

    def convertToJson(self):
        """
        Converts a message to json
        :return: the converted message
        """
        to_return = {
            'id': self.id,
            'payload': self.payload
        }
        return json.dumps(to_return)