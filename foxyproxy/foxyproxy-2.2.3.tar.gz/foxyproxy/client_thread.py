#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
***
Module: client_thread - Implementation of the proxy request processing
***
"""

# Copyright (C) Smart Arcs Ltd, Enigma Bridge Ltd, registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018

import logging
import threading
import time

from foxyproxy.csp import BaseCryptoService
from foxyproxy.request_data import RequestData

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)
# fh = logging.FileHandler('foxyproxy.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)


class ClientThread(threading.Thread):
    """
    Function for handling connections. This will be used to create threads
    """
    def __init__(self, protocol, connection, signer):
        """
        :param protocol: a type of the connection to correctly send the response asynchronously: TCP, REST, WS
        :type protocol: str
        :param connection: the opened connection for response
        :type connection: socket object
        :param signer: reference of the signer
        :type signer: BaseCryptoService
        """
        threading.Thread.__init__(self)
        self.connection = connection
        self.signer = signer
        self.protocol = protocol.lower()
        self.response = ""

    def run(self):
        """
        Thread body - selects TCP or REST processing
        :return:
        """

        if self.protocol == 'tcp':
            self.run_tcp()
        else:
            self.run_service()

    def run_tcp(self):
        """
        A TCP request processing method
        :return:
        """
        try:
            # infinite loop so that function do not terminate and thread do not end.
            while True:
                # Receiving from client
                reader = None
                password = None
                commands = []
                # first we read all the commands
                data_raw = self.connection.recv(4096)
                if len(data_raw) == 0:  # connection was closed
                    break
                buffer_list = None
                try:
                    # buffer_list.append(data_raw)
                    if buffer_list is None:
                        buffer_list = data_raw
                    else:
                        buffer_list += data_raw
                except TypeError:
                    logging.error("Received data can't be converted to text")
                    pass

                # data = ''.join(buffer_list)
                data = buffer_list.decode('utf-8')

                # data = ">Simona /111.222.123.033@07|\n>2:RESET|\n>3:APDU:1100000000|\n>4:APDU:2200000000|" \
                #        "\n>5:APDU:3300000000|"
                # data = ">K|\n>3:SIGN:0000000000000000000000000000000000000000|"
                lines = data.splitlines()
                for line in lines:
                    line = line.strip()  # remove white space - beginning & end
                    if line[0] == '#':
                        # this may be in internal info
                        pass
                    elif line[0] != '>':
                        # we will ignore this line
                        continue
                    line = line[1:].strip()  # ignore the '>' and strip whitespaces
                    if line.rfind('|') < 0:
                        logging.info("Possibly missing | at the end of the line %s " % line)
                    else:
                        line = line[:line.rfind(u"|")]
                    if not reader:
                        cmd_parts = line.split(u':')
                        reader = cmd_parts[0]  # if '|' is not in string, it will take the whole line
                        if len(cmd_parts) > 1:
                            password = cmd_parts[1]
                    else:
                        cmd_parts = line.split(':')
                        if len(cmd_parts) < 2 or len(cmd_parts) > 4:
                            logging.error('Invalid line %s - ignoring it' % line)
                            continue

                        item = {'id': cmd_parts[0], 'name': cmd_parts[1], 'bytes': None, 'object': None}
                        if len(cmd_parts) > 2:
                            item['bytes'] = cmd_parts[2]
                        if len(cmd_parts) > 3:
                            item['object'] = cmd_parts[3]
                        commands.append(item)

                if len(commands) == 0:
                    logging.error("No commands to process")
                    time.sleep(0.1)  # sleep little before making another receive attempt
                    continue

                for command in commands:
                    input_req = RequestData(reader,
                                            command['id'],
                                            command['name'],
                                            command['bytes'],
                                            command['object'],
                                            password=password)

                    ########
                    response_data = self.process_command(input_req)
                    #########
                    response = ">{0}{1}{2}{3}\n".format(input_req.command_id,
                                                        BaseCryptoService.CMD_SEPARATOR,
                                                        response_data,
                                                        BaseCryptoService.CMD_RESPONSE_END)

                    self.response = response.encode("utf-8")
                    logging.info(self.response)
                    self.connection.sendall(self.response)
                # break  # we close the connection after
        except Exception as ex:
            logging.info('Exception in serving response (1), ending thread %s' % ex)
            logging.info('\n')

        # Terminate connection for given client (if outside loop)
        self.connection.close()
        return

    def run_service(self):
        """
        The main service loop
        :return:
        """
        try:
            # infinite loop so that function do not terminate and thread do not end.
            # Receiving from client
            reader = None
            password = None
            commands = []
            # first we read all the commands
            data_json = self.connection

            if not data_json:  # connection was closed
                return

            if "reader" not in data_json or (('command' not in data_json) and ('commands' not in data_json)):
                logging.info("JSON structure is in correct, it must have 'reader' and 'command'/'commands'")
                return

            # JSON will have the following structure
            #  {
            #       "reader": "Simona /111.222.123.033@07",
            #       "commands": [
            #           { "nonce": "2",
            #             "line": "RESET" },
            #           { "nonce": "3",
            #             "line": "APDU:1100000000" }
            #       ],
            #       "command": {"nonce": "2",
            #                   "line": "RESET"}
            #  }

            reader = data_json['reader']

            if 'password' in data_json:  # this is not currently used
                password = data_json['password']
            else:
                password = None

            if "command" in data_json:
                command = data_json['command']

                if ("id" in command) and ("line" in command):
                    cmd_id = command['id']
                    cmd_line = command['line']
                    cmd_parts = cmd_line.split(':')
                    if len(cmd_parts) < 1 or len(cmd_parts) > 3:
                        logging.error('Invalid line %s - ignoring it' % cmd_line)
                    else:
                        item = {'id': cmd_id, 'name': cmd_parts[0], 'bytes': None, 'object': None}
                        if len(cmd_parts) > 1:
                            item['bytes'] = cmd_parts[1]
                        if len(cmd_parts) > 2:
                            item['object'] = cmd_parts[2]
                        commands.append(item)
                else:
                    logging.info("The 'command' element has a missing 'id' or 'line'")

            if "commands" in data_json:
                for each_cmd in data_json['commands']:
                    if ("id" in each_cmd) and ("line" in each_cmd):
                        cmd_id = each_cmd['id']
                        cmd_line = each_cmd['line']
                        cmd_parts = cmd_line(':')
                        if len(cmd_parts) < 1 or len(cmd_parts) > 3:
                            logging.error('Invalid line %s - ignoring it' % cmd_line)
                        else:
                            item = {'id': cmd_id, 'name': cmd_parts[0], 'bytes': None, 'object': None}
                            if len(cmd_parts) > 1:
                                item['bytes'] = cmd_parts[1]
                            if len(cmd_parts) > 2:
                                item['object'] = cmd_parts[2]
                            commands.append(item)
                    else:
                        logging.info("An item in 'commands' element has a missing 'id' or 'line'")

            if len(commands) == 0:
                logging.error("No commands to process")
                return

            response_json = []
            for command in commands:
                input_req = RequestData(reader,
                                        command['id'],
                                        command['name'],
                                        command['bytes'],
                                        command['object'],
                                        password=password)

                ########
                response_data = self.process_command(input_req)
                #########
                one_item = {
                    "id": input_req.command_id,
                    "line": response_data
                }
                response_json.append(one_item)

                to_return = {
                    "response": response_json
                }
                self.response = to_return
                logging.info(self.response)
        except Exception as ex:
            logging.info('Exception in serving response (2), ending thread %s' % ex)
            logging.info('\n')

        return

    def process_command(self, input_req):
        """
        Processes command that has been successfully parsed.
        :param input_req:
        :type input_req: RequestData
        :return:
        """
        logging.info(u"Reader:'{0}',CommandID:'{1}',Command:'{2}'"
                     .format(input_req.reader_name, input_req.command_id, input_req.command_name))

        processing_command = input_req.command_name.upper()

        # SEND APDU
        if processing_command == BaseCryptoService.CMD_APDU:
            token_name = BaseCryptoService.decode_cf_reader(input_req.reader_name)
            response_data = self.signer.apdu(token_name, input_req.command_data)
        # get CHAIN
        elif processing_command == BaseCryptoService.CMD_CHAIN:
            # reader_name = Alias
            response_data = self.signer.chain(input_req.reader_name)
        # ALIAS
        elif processing_command == BaseCryptoService.CMD_ALIAS:
            aliases = self.signer.aliases()
            response_data = "|".join(aliases)
        # ENUM - get names of all connected tokens
        elif processing_command == BaseCryptoService.CMD_ENUM:
            readers = self.signer.tokens(input_req.reader_name, input_req.command_data)
            response_data = "|".join(readers)
        # SIGN
        elif processing_command == BaseCryptoService.CMD_SIGN:
            response_data = self.signer.sign(input_req.reader_name, input_req.command_data, input_req.password)
        # RESET
        elif processing_command == BaseCryptoService.CMD_RESET:
            token_name = BaseCryptoService.decode_cf_reader(input_req.reader_name)
            response_data = self.signer.reset(token_name)

        else:  # No valid command found
            response_data = BaseCryptoService.CMD_RESPONSE_FAIL

        return response_data

    def get_response(self):
        """
        A simple getter for response
        :return:
        """
        return self.response
