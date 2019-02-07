#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
import base64
import datetime
import logging
import os
import platform
import re

# from typing import List, Any

from foxyproxy.upstream import BaseUpstream

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)


class BaseCryptoService(object):
    """
    The abastract class for crypto service providers - definitions of functions working with smartcards.
    """
    server = None  # type: BaseUpstream
    CMD_APDU = "APDU"
    CMD_RESET = "RESET"  # requests smartcard reset
    CMD_SIGN = "SIGN"  # requests eIDAS signature
    CMD_CHAIN = "CHAIN"  # requests certificate chain from a given smart card
    CMD_ALIAS = "ALIASES"  # requests all names from certificates
    CMD_ENUM = "ENUM"  # requests a list of readers

    CMD_SEPARATOR = ":"
    CMD_LINE_SEPARATOR = "|"
    CMD_RESPONSE_END = "\n@@"

    CMD_NO_CARD = "C080"  # no card - from upstream
    CMD_RESPONSE_FAIL = "C081"
    CMD_VAGUE_NAME = "C082"
    CMD_READER_NOT_FOUND = "C083"
    CMD_READER_WRONG_DATA = "C084"
    CMD_READER_WRONG_PIN = "C085"
    CMD_UPSTREAM_ERROR = "C086"
    CMD_INTERNAL_ERROR = "C090"
    CMD_OK = "9000"

    def __init__(self, server):
        """
        The constructor shows a set of suggested data structures
        :param server: this is a configuration of the upstream server, or process this proxy connects to
        :type server: BaseUpstream
        """

        # connection details for the signing server
        self.server = server
        self.storage = BaseCryptoServiceStorage()
        self.initialized = False

        # we also create a user configuration folder
        # first we read certificates from the user's home folder
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, r'.cloudfoxy')
        if platform.system() == 'Windows':
            self.user_dir = os.path.join(home_dir, r'CloudFoxy')
        elif platform.system() == 'Darwin':
            self.user_dir = os.path.join(home_dir, r'CloudFoxy')
        else:
            self.user_dir = os.path.join(home_dir, r'CloudFoxy')

        self.cert_dir = os.path.join(config_dir, r'certs')
        self.token_dir = os.path.join(config_dir, r'tokens')
        self.inbox_dir = os.path.join(config_dir, r'inbox')
        self.outbox_dir = os.path.join(config_dir, r'outbox')
        if not os.path.exists(self.cert_dir):
            os.makedirs(self.cert_dir)
        elif not os.path.isdir(self.cert_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.cert_dir)
            exit(4)
        if not os.path.exists(self.token_dir):
            os.makedirs(self.token_dir)
        elif not os.path.isdir(self.token_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.cert_dir)
            exit(4)
        if not os.path.exists(self.inbox_dir):
            os.makedirs(self.inbox_dir)
        elif not os.path.isdir(self.inbox_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.inbox_dir)
            exit(4)
        if not os.path.exists(self.outbox_dir):
            os.makedirs(self.outbox_dir)
        elif not os.path.isdir(self.outbox_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.outbox_dir)
            exit(4)
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        elif not os.path.isdir(self.user_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.user_dir)
            exit(4)

    def init(self, config=None):
        """
        Initialization function, which will be called periodically by a scheduler. It does any necessary
        initialization of the csp signing provider as well as reacts to changes.
        :param config: configuration data, as appropriate for a given csp provider
        :return:
        """
        raise NotImplementedError("Please Implement the method 'init'")

    def sign(self, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        """
        The actual signing function. It needs two parameters: fingerprint, and alias. The alias is the name
        to look-up a key, fingerprint is a hex-encoding fingerprint. It also accepts 2 optional parameter
        :param alias: an identification of the key - e.g., a name on the relevant certificate.
        :type alias: str
        :param fingerprint: a hex-encoded data that will be signed,
        :type fingerprint: str
        :param password: an optional password needed to obtain access to the signing key
        :type password: str
        :param sign_alg: identifier of the signing algorithm - if not specified, it shall be RSA
        :type sign_alg: int
        :param hash_alg: identifier of the hash algorithm used to create the fingerprint; if not specified, it will
                         be one of SHA functions derived from the length of the fingerprint
        :type hash_alg: int
        :return: the signature of the 'fingerprint' using the sign_alg and a key identified by the alias
        :rtype: str the signature in hex encoding - each 8bits are encoded as two characters of 0-9a-f
        """

        raise NotImplementedError("Please Implement the method 'sign'")

    def aliases(self):
        """
        This function provides a list of names to identify signing keys/certificates. It doesn't take any parameters
        :return: A list of key/certificate aliases, e.g., names of persons whose keys are available
        ":rtype: list of str
        """
        raise NotImplementedError("Please Implement the method 'aliases'")

    def chain(self, alias, sign_alg=None):
        """
        This function returns a complete chain of certificates for a given alias and an optional sign_alg, e.g., RSA.
        The list should not contain the "root" certificate. The order is from the certificate signed by a root
        certificate. The last certificate is the certificate issued for the "alias".
        :param alias: An identifier that can be used to identify the required certificate chain.
        :type alias: str
        :param sign_alg is an optional parameter, which can help identify the correct set of certificates if a given
                        alias has keys for more than one signing algorithm
        :type sign_alg: int
        :return: a list of hex-encoded certificates in the correct order - parent certificate precedes the certificate
                 it signed
        :rtype: list of string
        """
        raise NotImplementedError("Please Implement the method 'chain'")

    def reset(self, token):
        """
        The method adds an ability to reset the token to return it to an initial state, if it's required
        :param token:
        :type token: string
        :return:
        """

        raise NotImplementedError("Please Implement the method 'reset'")

    def apdu(self, token, command):
        """
        Execute any of the atomic operations available from the token
        :param token: identification of the token
        :type token: str
        :param command: a complete command, in hex-encoding
        :type command: str
        :return: a hex-encoded response from the token
        :rtype str:
        """
        raise NotImplementedError("Please Implement the method 'reset'")

    # #########################################################################
    # the remaining methods are already implemented
    # #########################################################################

    def check_response(self, response, reader, message, index=0, error=1):
        """

        :param response: response received from the upstream signer
        :param reader: name of the response source
        :param message: text message that should be logged when there's an error
        :param index: the line of the response that should be processed
        """
        response_data = None

        if response is None:
            if error:
                logging.error("%s: %s %s - no response" % (type(self).__name__, message, reader))
            else:
                logging.debug("%s: %s %s - no response" % (type(self).__name__, message, reader))
            response_data = BaseCryptoService.CMD_UPSTREAM_ERROR
        else:
            if not isinstance(response, list):
                response = [response]

            # response processing
            if len(response) <= index:  # index=0 -> we need at least len() = 1
                if error:
                    logging.error("%s: %s, reader: %s - response array too small as requested %d (%s)"
                                  % (type(self).__name__, message, reader, index, response))
                else:
                    logging.debug("%s: %s, reader: %s - response array too small as requested %d (%s)"
                                  % (type(self).__name__, message, reader, index, response))

                response_data = BaseCryptoService.CMD_INTERNAL_ERROR
            elif len(response[index]) < 4:
                if error:
                    logging.error("%s: %s, reader: %s - code: %s"
                                  % (type(self).__name__, message, reader, response[index]))
                else:
                    logging.debug("%s: %s, reader: %s - response array too small as requested %d (%s)"
                                  % (type(self).__name__, message, reader, index, response))
                response_data = BaseCryptoService.CMD_UPSTREAM_ERROR
            elif response[index][-4:] != "9000":
                if error:
                    logging.error("%s: %s, reader: %s - code: %s"
                                  % (type(self).__name__, message, reader, response[index]))
                else:
                    logging.debug("%s: %s, reader: %s - code: %s"
                                  % (type(self).__name__, message, reader, response[index]))
                response_data = response[index][-4:]

        if response_data:
            response_data = response_data.upper()

        return response_data

    @staticmethod
    def unix_time(dt):
        """
        Get a unix_time regardless of the timezone
        :param dt:
        :return:
        """
        if dt is None:
            return None
        cur = datetime.datetime.utcfromtimestamp(0)
        if dt.tzinfo is not None:
            cur.replace(tzinfo=dt.tzinfo)
        else:
            cur.replace(tzinfo=None)
        # noinspection PyBroadException
        try:
            return (dt - cur).total_seconds()
        except Exception:
            pass

    def downtime(self):
        """
        Returns true if the terminal / server of terminals has been restarted
        :return:
        """
        return self.server.downtime()

    def tokens(self, regex_name, maximum=0):
        """
        No parameters, returns a list of readers
        :return:
        """
        readers = []
        counter = 0
        for one_name in self.storage.cert_names:
            name = BaseCryptoService.encode_cf_reader(one_name['reader'])
            user = one_name['name']
            priority = one_name['priority']
            if (len(regex_name) == 0) or (re.match(regex_name, name)) or (re.match(user, name)):
                if (maximum > 0) and (counter >= maximum):
                    already_in = None
                    for already_in in readers:
                        if already_in['priority'] < priority:
                            break
                    if already_in and (already_in['priority'] < priority):
                        readers.remove(already_in)
                        readers.append(base64.b64encode(name.encode('utf-8')).decode('ascii'))
                else:
                    readers.append(base64.b64encode(name.encode('utf-8')).decode('ascii'))
                    counter += 1
                break

        return readers

    def prioritize(self, regex_name):
        """
        Make one more terminals show at the top of a list of terminals  returned by ENUM
        :param regex_name:
        :return:
        """
        for one_name in self.storage.cert_names:
            name = BaseCryptoService.encode_cf_reader(one_name['reader'])
            user = one_name['name']
            if (len(regex_name) > 0) and (re.match(regex_name, name) or re.match(user, name)):
                self.storage.last_priority += 1
                one_name['priority'] = self.storage.last_priority

        self.storage.cert_names.sort(key=BaseCryptoService._cert_names_sort, reverse=True)

        return_list = []
        if self.storage.cert_names is not None:
            for one_name in self.storage.cert_names:
                return_list.append("%s (%s)" % (one_name['reader'], one_name['short_name']))

        return return_list

    @staticmethod
    def _cert_names_sort(e):
        return e['priority']

    def get_certs(self, reader_id):
        """
        Returns a string of certificates in the correct format for FoxyProxy
        :param reader_id: e.g., /192.168.42.10@1
        :return:
        """
        str_certs = ""
        if reader_id in self.storage.certificates.keys():
            str_certs += self.storage.certificates.get(reader_id)['cert'].decode('ascii')
            for ca_cert in self.storage.certificates.get(reader_id)['chain']:
                str_certs += ":" + ca_cert['cert'].decode('ascii')

        return str_certs

    def get_token(self, subject):
        """
        Accepts names of certificate owners and returns a list of readers that have certs with this string in cert names
        :param subject: a substring of a name from a certificate
        :return:
        """
        token = []
        for one_name in self.storage.cert_names:
            if subject in one_name['name']:
                token.append(one_name)

        return token

    @staticmethod
    def encode_cf_reader(name):
        """
        Adds decoration to CloudFoxy reader names
        :type name: str
        """
        if name[0] == '/' and name.find('@') > 1:
            name = "CloudFoxy NET " + name[1:]  # also remove the '/' at the beginning
            name = name.replace('@', '-')
        else:
            name = "CloudFoxy USB " + name
        return name

    @staticmethod
    def decode_cf_reader(name_in):
        """
        Removes a decoration from CloudFoxy reader names.
        :type name_in: str
        """
        prefix_net = "CloudFoxy NET"
        prefix_usb = "CloudFoxy USB"
        name = name_in.strip()
        if name.find(prefix_net) == 0:  # network name - strip prefix, add '/' and replace '-' with '@'
            name = '/' + name[len(prefix_net):]
            name = name.replace('-', '@')
        elif name.find(prefix_usb) == 0:  # local/usb name - strip prefix only
            name = name[len(prefix_usb):]

        logging.debug(u'Updating token name {0} to {1}'.format(name_in, name))

        return name


class BaseCryptoServiceStorage(object):
    """
    Storage of smartcard data for the base class.
    """
    cert_names = None  # type: List[Any]

    def __init__(self):
        # this is a hash table of certificates we need to initialize now
        # the key is a name of the token, values are {'cert': <certificate}, 'chain': []}
        self.certificates = {}

        # this will contain a mapping from names to tokens {name:<>, reader:<>}
        self.cert_names = []

        # for future use - a hash map - list of CA certs on a token
        # possibly for appending to signatures if tokens do not have certificates
        self.card_cas = {}

        self.last_priority = 0  # this will increment with each request to show a particular terminal in ENUM command
        pass

    def reset(self):
        """
        Reset a smart-card.
        """
        raise NotImplementedError("Please Implement the method 'reset' in your CSP module")

    def initialize(self):
        """
        Initialize the storage = forget all the information about smartcards so we can re-read it.
        """
        self.certificates = {}
        self.cert_names = []
        self.card_cas = {}
        self.last_priority = 0
