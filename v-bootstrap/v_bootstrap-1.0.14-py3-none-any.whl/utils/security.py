import os
import logging

from . import get_tool_dir

logger = logging.getLogger(__name__)

_SECURITY_OUTPUT_DIR = os.path.join(get_tool_dir(), 'security')

_SECURITY_CERT_NAME = 'oem-client.pem'
_SECURITY_PUB_NAME = 'public_key.pem'
_SECURITY_KEY_NAME = 'private_key.pem'

_SECURITY_CERT_PATH = os.path.join(_SECURITY_OUTPUT_DIR, _SECURITY_CERT_NAME)
_SECURITY_PUB_PATH = os.path.join(_SECURITY_OUTPUT_DIR, _SECURITY_PUB_NAME)
_SECURITY_KEY_PATH = os.path.join(_SECURITY_OUTPUT_DIR, _SECURITY_KEY_NAME)

_SERVER_MERGED_CERT = os.path.join(_SECURITY_OUTPUT_DIR, '.server.cred.pem')


def get_security_dir():
    return _SECURITY_OUTPUT_DIR


def default_cert():
    """ Returns default client cert. """
    return _SECURITY_CERT_PATH


def keys_exist(output=_SECURITY_OUTPUT_DIR):
    """ Checks a key pair. """
    pub_file = os.path.join(output, _SECURITY_PUB_NAME)
    key_file = os.path.join(output, _SECURITY_KEY_NAME)

    logger.debug("Checking the keys:\n%s\n%s", pub_file, key_file)
    if os.path.isfile(pub_file) or os.path.isfile(key_file):
        return True

    return False


def save_keys(public, private, output=_SECURITY_OUTPUT_DIR):
    """ Saves a key pair content in files. """
    if not os.path.exists(output):
        os.makedirs(output)

    logger.debug("Saving the keys in %s", output)

    pub_file = os.path.join(output, _SECURITY_PUB_NAME)
    with open(pub_file, 'wb') as cert:
        cert.write(public)

    key_file = os.path.join(output, _SECURITY_KEY_NAME)
    with open(key_file, 'wb') as key:
        key.write(private)


def merge_certs(cert, key=_SECURITY_KEY_PATH):
    """ Appends a private key to certs. """
    with open(cert, "rb") as c, open(key, "rb") as k:
        cert_cont = c.read()
        key_cont = k.read()

    with open(_SERVER_MERGED_CERT, "wb+") as m:
        m.write(cert_cont + os.linesep.encode())
        m.write(key_cont)

    return _SERVER_MERGED_CERT


class PubKeys(object):
    """ A container for online/offline key pairs. """
    TYPE_ONLINE = 'online'
    TYPE_OFFLINE = 'offline'
    TYPES = (TYPE_ONLINE, TYPE_OFFLINE)

    def __init__(self):
        self._online = None
        self._offline = None

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, value):
        self._online = value

    @property
    def offline(self):
        return self._offline

    @offline.setter
    def offline(self, value):
        self._offline = value
