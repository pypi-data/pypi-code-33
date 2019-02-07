# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: ica - Implementation of the I.CA signer API
***
"""

# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018

import base64
import binascii
import logging
import time

from cryptography import x509
from cryptography.hazmat.backends import default_backend
# noinspection PyProtectedMember
from cryptography.x509 import ExtensionOID

from foxyproxy.csp import BaseCryptoService
from foxyproxy.upstream import RegisterUpstream

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)


class CryptoICA(BaseCryptoService):
    """
    This class implements signing with eIDAS smart cards of a Czech trust provider I.CA.
    """

    def __init__(self, cmd_params):

        server = RegisterUpstream.get_service(cmd_params['upstream'], token=cmd_params['token'],
                                              signer=cmd_params['signer'])
        if server is None:
            logging.error("No upstream server configuration created")
            exit(-1)

        if cmd_params['register']:
            self.create_csr = True
        else:
            self.create_csr = False

        # we call the super() constructor to initialize the 'self.signer' object
        super(CryptoICA, self).__init__(server)

    def init(self, config=None):
        """
        Initialize data for upstream signer and read all available certificates
        :param config:
        """
        is_down = False
        while self.server.is_down():
            is_down = True
            time.sleep(2)  # try in 2 seconds

        if is_down:
            logger.info("Upstream server connected")

        was_down = self.server.downtime()

        if was_down:
            # we refresh the crypto storage
            self.storage.initialize()
            self._read_certificates()
            self.server.set_uptime()
        pass

    def aliases(self):
        """
        Extracts names from cerificates and returns them as a list
        :return:
        """
        all_names = []
        for each_name in self.storage.cert_names:
            all_names.append(base64.b64encode(each_name['name'].encode('utf-8')).decode('ascii'))
        return all_names

    def chain(self, alias, sign_alg=None):
        """
        Returns a chain of certificates for a given alias
        :param alias:
        :param sign_alg:
        :return:
        """
        reader = self.get_token(alias)
        if len(reader) != 1:
            if len(reader) == 0:
                # we haven't found the name
                response_data = BaseCryptoService.CMD_READER_NOT_FOUND
            else:
                # the name is not unique
                response_data = BaseCryptoService.CMD_VAGUE_NAME
        else:
            # and we need to get the certificate chain
            response_data = self.get_certs(reader[0]['reader'])
        return response_data

    def sign(self, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        """
        The actual signing on the upstream signer. It checks the password/PIN if not None
        :param alias: name from the certificate
        :param fingerprint: the data to sign
        :param password: PIN/password to unlock the signer
        :param hash_alg: string identification of the hash algorithm
        :param sign_alg: string identification of the signing algorithm
        :return: strig with error code / data
        """
        # signing consists of the following APDUs
        # apdu=00A4000C023F00\&reset=1  - card reset
        # apdu=00A4010C020604           - select of the PIN file
        # apdu=002000810733323837313935  - PIN check  - 3287295
        # apdu=00 22 41 AA 04 89 02 14 30   . 41 - MSE:SET, AA - hash,
        #                      89021430 = sha-256, 89021410 = sha-1
        # apdu=00 22 41 B6 0A 84(SDO ref) 03 800400 8903 13 23 30 -
        #                      8903132330 - rsa-sha-256, 8903132310 = rsa-sha1
        # apdu=00 2A 90 A0 22 90 20 D0 6C EF 8B 4A DA 05 75 9E 1A 2C 75 23 64 15 08 DC BA 5C B6 E7 C3
        # 3F E8 A2 C6 43 C0 1B C4 CE 34

        reader = self.get_token(alias)
        if len(reader) != 1:
            if len(reader) == 0:
                # we haven't found the name
                response_data = BaseCryptoService.CMD_READER_NOT_FOUND
            else:
                # the name is not unique
                response_data = BaseCryptoService.CMD_VAGUE_NAME
            return response_data

        # we have a reader, let's do the signing
        if len(fingerprint) == 40:
            sha_id = "10"
        elif len(fingerprint) == 64:
            sha_id = "30"
        else:
            response_data = BaseCryptoService.CMD_READER_WRONG_DATA
            return response_data

        self.server.cmd('00A4000C023F00', reader[0]['reader'], 1)
        response_all = self.server.cmd('00A4010C020604', reader[0]['reader'])

        response_data = self.check_response(response_all, reader[0]['reader'], "Selection before signing failed")
        if response_data is not None:
            return response_data

        # PIN
        # if the password is set
        # pin_ok = True
        password_command = None
        if password is not None:
            encoded_password = binascii.b2a_hex(password.encode('ascii')).decode('ascii')
            if (reader[0]['pin'] is not None) and (reader[0]['pin'] == encoded_password):
                logger.error("Blocked repeated use of incorrect PIN at reader %s, remaining tries %s"
                             % (reader[0]['reader'], response_all[-1:]))
                # pin_ok = False
                response_data = BaseCryptoService.CMD_READER_WRONG_PIN
            else:
                password_command = '00200086%02X%s' % (len(password), encoded_password)
                response_all = self.server.cmd(password_command, reader[0]['reader'])

                response_data = self.check_response(response_all, reader[0]['reader'], "Error verifying PIN")
                if response_data is None:  # all good
                    reader[0]['pin'] = None

                    # different versions of card need different PIN version
                    password_command = '00200081%02X%s' % (len(password), encoded_password)
                    response_all = self.server.cmd(password_command, reader[0]['reader'])
                    response_data = self.check_response(response_all, reader[0]['reader'], "Error verifying PIN2")

                elif response_data[-4:-1] == "63C":  # we test only 3 out of 4 status digits
                    # there is a problem with PIN - the counter of remaining tries is returned
                    logger.error("Incorrect PIN to reader %s, remaining tries %s" %
                                 (reader[0]['reader'], response_all[0][-1:]))
                    reader[0]['pin'] = encoded_password
                    # pin_ok = False
                    response_data = BaseCryptoService.CMD_READER_WRONG_PIN

        if response_data is None:
            # let's do signing - we may try a few times if 'file_id' is not set
            keep_trying = True
            response_data = None
            temp_file_id = reader[0]['file_id']

            key_id_limit = 15
            if temp_file_id == 0:
                temp_file_id = key_id_limit
            while keep_trying:
                # h MSE:Set sha-256
                self.server.cmd('002241AA04890214%s' % sha_id, reader[0]['reader'])
                # h MSE:Set DST
                response_all = self.server.cmd('002241B60A 840380%02X00 89031323%s' % (temp_file_id, sha_id),
                                               reader[0]['reader'])

                response_data = self.check_response(response_all, reader[0]['reader'], "Error setting MSE DST reader")

                # send the hash to the card
                sha_length = int(len(fingerprint) / 2)
                if response_data is None:
                    response_all = self.server.cmd('002a90a0%02X90%02X%s' % (sha_length + 2, sha_length, fingerprint),
                                                   reader[0]['reader'])
                    response_data = self.check_response(response_all, reader[0]['reader'],
                                                        "Error sending hash to signing terminal")
                # else:
                #     keep_trying = False

                if response_data is None:
                    # finally, request signing and collect the signature
                    response_all = self.server.cmd("002A9E9A00", reader[0]['reader'])
                    response_data = self.check_response(response_all, reader[0]['reader'],
                                                        "Signing unsuccessful", error=0)

                    if response_data is None:  # success
                        if reader[0]['file_id'] == 0:
                            self._update_file_id(reader[0], temp_file_id)
                        response_data = response_all[0][0:-4]

                        keep_trying = False
                    elif (response_data != "9000") and (response_data != BaseCryptoService.CMD_INTERNAL_ERROR):
                        # let's see if we should try again
                        if reader[0]['file_id'] == 0 and key_id_limit > 0:
                            key_id_limit -= 1
                            temp_file_id -= 1
                        else:
                            keep_trying = False
                    else:
                        # we found an internal error - probabbly not worth trying again
                        pass
                else:
                    # let's see if we should try again
                    if reader[0]['file_id'] == 0 and key_id_limit > 0:
                        key_id_limit -= 1
                        temp_file_id -= 1
                    else:
                        keep_trying = False

        return response_data

    def apdu(self, signer_name, command):
        """
        A native command provided by the cryptographic token
        :param signer_name: identification of the cryptographic token, e.g., smartcard
        :type signer_name: str
        :param command: the actual command - hex encoded
        :type command: str
        :return:
        """

        response_all = self.server.cmd(command, signer_name)
        if len(response_all) > 0:
            response_data = response_all[0]
        else:
            response_data = BaseCryptoService.CMD_INTERNAL_ERROR
        return response_data

    def reset(self, signer_name):
        """
        Request reset of a given upstream signer.
        :param signer_name: identification of the cryptographic token, e.g., smartcard
        :type signer_name: str
        :return: response -> ATR if all good
        """
        response_all = self.server.cmd(None, signer_name, 1)
        if len(response_all) > 0:
            response_data = response_all[0]
        else:
            response_data = BaseCryptoService.CMD_INTERNAL_ERROR

        return response_data

    # #########################################################################
    #  Internal methods
    # #########################################################################

    def _read_certificates(self):

        # let's now get a list of card readers and ATRs
        response_data = self.server.inventory()

        total_cards = 0
        for each_line in response_data:
            total_cards += 1
            logging.info("Found a new chip '%s'" % each_line)
            # it may contain ATR, let's see if it does
            last_sep = each_line.split()
            # if ATR, first character in the last item will start with '3B'
            last_part = len(last_sep) - 1
            if last_sep[last_part].upper().startswith('3B'):
                items = [each_line[:-len(last_sep[last_part])].strip()]
            else:
                items = [each_line]

            # we found a smart-card
            self.storage.certificates[items[0]] = {}  # we need to get the certificates

        if total_cards < 1:
            logger.error("%d chips found" % total_cards)
        else:
            logger.debug("%d chips found - we inspect presence of certificates now" % total_cards)
        # now, let's query smart cards
        # 1. we select folder with certificates
        #    A4 02 0C 02 56 30
        #    and request all items
        #    00 B2 xx 04 00/FF   // where xx goes from 1, till we get and error "6A 83"
        #    we parse each response 01 xx (if length < 0x82) ...
        #       01 xx ..... 02 04 ... 10 04 ff ff aa aa -> FOLDER/FILE .... 12 04 00 ll ll -> ll ll = cert length
        # 2. we load the certificate
        #    00 A4 00 0C 02 3F 00
        #    00 A4 01 0C 02 3F 50
        #    00 A4 01 0C 02 ff ff
        #    00 A4 01 0C 02 aa aa
        #    and read the cert with 00 B0 xx 00 00, where xx = 0 ... x
        # 3. we parse certificates - find user certs and their chains
        # 4. store in a hash map
        for reader in self.storage.certificates.keys():

            ##########################
            # a new approach to derive the file ID for the private key
            ##########################
            error = False
            response_all = self.server.cmd('00A4000C023F00', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd('00A4010C023F50', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd('00A4010C023F10', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd('00A4020C025660', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True

            cert_file_id = 1
            not_found = True
            while not_found and not error:
                response_all = self.server.cmd('00B2%02X0400' % cert_file_id, reader)  # a folder
                # print(response_all[0])
                if len(response_all) < 1 or response_all[0][-4:] != "9000":
                    cert_file_id -= 1  # the previous one was the last good
                    not_found = False
                else:
                    cert_file_id += 1

            ##########################
            ##########################

            latest_cert_time = 0
            self.storage.card_cas[reader] = []
            self.server.cmd('00A40004023F0000', reader, 1)

            new_item = True
            certificate_id = 1
            end_subject = ""
            end_issuer = ""

            subject_cn = None
            while new_item:
                response_all = self.server.cmd('00A4000C023F00', reader)  # switch to the app
                response_all = self.server.cmd('00A4010C023F50', reader)  # select files with objects
                response_all = self.server.cmd('00A4010C023F10', reader)  # we need a directory structure
                response_all = self.server.cmd('00A4020C025630', reader)   # and a list of certificates

                if self.check_response(response_all, reader, "00A4020C025630 error") is not None:
                    break

                # select 1..n-th certificate record
                apdu = '00B2%02X0400' % certificate_id
                certificate_id += 1
                response_all = self.server.cmd(apdu, reader)

                if self.check_response(response_all, reader, "00B2%02X0400 error" % certificate_id, error=0) is not None:
                    break

                # keep the first line without the last 4 characters
                raw_response = bytearray.fromhex(response_all[0][:-4])  # remove the first ASN.1 tag
                if raw_response[1] <= 0x81:
                    raw_response = raw_response[2:]  # ... and its length
                else:
                    offset = (raw_response[1] - 128) + 2  # ... and its length, we only keep the value
                    raw_response = raw_response[offset:]  # the long length encoding 01 82 xx xx
                file_id = None
                cert_len = 0
                while (len(raw_response) > 2) and ((file_id is None) or (cert_len == 0)):
                    if raw_response[0] == 0x10:  # this is 2 file descriptors to select a certificate
                        file_id = raw_response[2:6]
                    if raw_response[0] == 0x12:  # this is the length of the certificate we expect
                        cert_len = ((raw_response[2]*256 + raw_response[3])*256 + raw_response[4])*256 + raw_response[5]
                    raw_response = raw_response[(2+raw_response[1]):]
                # let's get a certificate now - first select one
                self.server.cmd('00A4000C023F00', reader)
                self.server.cmd('00A4010C023F50', reader)
                apdu = "00A4010C02%s" % binascii.b2a_hex(file_id[0:2]).decode('ascii')  # select cert folder /3f20
                self.server.cmd(apdu, reader)
                apdu = "00 a4 020C02%s" % binascii.b2a_hex(file_id[2:4]).decode('ascii')  # and the cert we want
                response_all = self.server.cmd(apdu, reader)

                if len(response_all) > 0 and response_all[0][-4:] == '9000':
                    counter = 0
                    new_cert = ""
                    while cert_len > 0:  # reading the cert - multiple APDUs
                        response_all = self.server.cmd('00B0%02X0000' % counter, reader)
                        if len(response_all) < 1 or response_all[0][-4:] != "9000":
                            break
                        new_cert += response_all[0][:-4]
                        cert_len -= (len(response_all[0])/2 - 2)
                        counter += 1

                    if cert_len <= 0:  # it should end up in cert_len == 0
                        # we got a cert
                        cert = x509.load_der_x509_certificate(binascii.a2b_hex(new_cert), default_backend())
                        subject_list = []
                        for attribute in cert.subject:
                            oid_in = attribute.oid
                            # dot = oid_in.dotted_string
                            # noinspection PyProtectedMember
                            oid_name = oid_in._name
                            val = attribute.value
                            subject_list.append('%s: %s' % (oid_name, val))
                            if oid_name.lower() == "commonname":
                                subject_cn = val
                        subject_list.sort()
                        subject = ', '.join(subject_list)
                        issuer_list = []
                        for attribute in cert.issuer:
                            oid_in = attribute.oid
                            # dot = oid_in.dotted_string
                            # noinspection PyProtectedMember
                            oid_name = oid_in._name
                            val = attribute.value
                            issuer_list.append('%s: %s' % (oid_name, val))
                        issuer_list.sort()
                        issuer = ', '.join(issuer_list)
                        ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
                        if ext and ext.value and ext.value.ca:
                            logging.debug("New CA certificate from reader %s: %s" % (reader, subject_cn))
                            # this is a CA, we store it in card CA list
                            self.storage.card_cas[reader].append({
                                'name': subject,
                                'issuer': issuer,
                                'cert': base64.standard_b64encode(binascii.a2b_hex(new_cert))
                            })
                        else:
                            logging.info("New user certificate from reader %s: %s" % (reader, subject_cn))
                            # it's an end-user certificate
                            issued_at = BaseCryptoService.unix_time(cert.not_valid_before)
                            if issued_at > latest_cert_time:
                                self.storage.certificates[reader]['cert'] = \
                                    base64.standard_b64encode(binascii.a2b_hex(new_cert))
                                end_issuer = issuer
                                end_subject = subject
                            else:
                                # we will only take the latest certificate - if there are more end-user certs
                                pass
                    else:
                        logging.error("Error reading a certificate from smart card, selector: %s" % apdu)

                else:
                    # cert file selection returned error
                    if len(response_all) > 0:
                        logging.error("Certificate file selection returned error: %s" % response_all[0])
                    else:
                        logging.error("Certificate file selection returned no response")

            # this is the end of reading certificates from smart card - we now need to create a chain
            # and extract the subject from the end-user cert
            if end_subject == "" or end_issuer == "":
                logging.error("No end-user certificate found on this smart card %s" % reader)
            else:
                # create a link from name to smart card
                self.storage.cert_names.append({
                    'name': end_subject,
                    'short_name': subject_cn,
                    'reader': reader,
                    'pin': None,
                    'priority': 0,
                    'file_id': 0})
                # we will try to find it with the first signature ...  end_cert_id})
                # let's create a chain
                root = False
                chain = []
                while not root:
                    next_found = False
                    for ca_cert in self.storage.card_cas[reader]:
                        if ca_cert['name'] == end_issuer:
                            next_found = True
                            chain.append(ca_cert)
                            end_issuer = ca_cert['issuer']
                            if ca_cert['name'] == ca_cert['issuer']:
                                root = True
                            break
                    if not next_found:
                        break
                if len(chain) < 1:
                    logging.error("No certificate found for %s" % end_subject)
                else:
                    self.storage.certificates[reader]['chain'] = chain

        pass

    def _update_file_id(self, reader, file_id):
        """
        If we find a correct file_id for the user's private key, we set it in the cert_names list
        :param reader: a copy of one of the items retrieved from cert_names
        :param file_id: an integer - the new file_id
        :return: None
        """
        new_cert_names = []
        for one_name in self.storage.cert_names:
            if reader['name'] == one_name['name']:
                one_name['file_id'] = file_id
            new_cert_names.append(one_name)
        self.storage.cert_names = new_cert_names
