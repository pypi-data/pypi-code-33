# -*- coding: utf-8 -*-
"""Encryption module."""

import os
import subprocess


class Gpg(object):
    """GnuPG encryptor class."""

    SECTION = 'Encrypt-GnuPG'

    def __init__(self, config):
        """
        Class constructor.

        :param config: Config object.
        :type config: :class:`ConfigParser.RawConfigParser`
        """
        self.cmd = config.get(self.SECTION, 'COMMAND', fallback='/usr/bin/gpg')
        self.recipient = config.get(self.SECTION, 'RECIPIENT', fallback=None)
        self.suffix = config.get(self.SECTION, 'SUFFIX', fallback='.gpg')
        self.open = open

    def encrypt(self, source, output=None):
        """
        Encrypt file.

        :param source: Path to file to encrypt.
        :type source: basestring
        :param output: Path to output encrypted file.
        :type output: basestring
        """
        params = [self.cmd, '--quiet', '--batch']
        if output is None:
            output = source + self.suffix
        params.append('--output')
        params.append(output)
        if self.recipient is not None:
            params.append('--recipient')
            params.append(self.recipient)
        else:
            params.append('--default-recipient-self')
        params.append('--encrypt')
        params.append(source)
        with self.open(os.devnull, 'w') as out:
            return subprocess.call(params, stderr=out)


ENCRYPTORS = {'gpg': Gpg}


def make_encryptor(name, config):
    """
    Create encryptor object.

    :param name: Name of encryptor to create.
    :type name: basestring
    :param config: Config object.
    :type config: :class:`ConfigParser.RawConfigParser`
    """
    if name not in ENCRYPTORS:
        raise Exception('Unknown encryptor: {}'.format(name))
    return ENCRYPTORS[name](config)
