
import logging
import re
import subprocess

from colibris import settings


DEVICE_SERIAL_NUMBER = 'DEVICE_SERIAL_NUMBER'
DEVICE_IP_ADDRESS = 'DEVICE_IP_ADDRESS'
DEVICE_MAC_ADDRESS = 'DEVICE_MAC_ADDRESS'
DEVICE_MAC_ADDRESS_UPPER = 'DEVICE_MAC_ADDRESS_UPPER'
DEVICE_FLASH_SIZE_KB = 'DEVICE_FLASH_SIZE_KB'

HOST_IP_ADDRESS = 'HOST_IP_ADDRESS'
HOST_IP_MASK_CIDR = 'HOST_IP_MASK_CIDR'
HOST_MAC_ADDRESS = 'HOST_MAC_ADDRESS'
HOST_MAC_ADDRESS_UPPER = 'HOST_MAC_ADDRESS_UPPER'

JOB_ID = 'JOB_ID'
TEST_CASE_NAME = 'TEST_CASE_NAME'


logger = logging.getLogger(__name__)
_attributes = {}


def set(name, value):
    _attributes[name] = value


def get(name, default=None):
    return _attributes.get(name, default)


def reset():
    _attributes.clear()


def discover():
    logger.debug('discovering attributes')

    _attributes[DEVICE_SERIAL_NUMBER] = settings.DEVICE_SERIAL_NUMBER
    _attributes[DEVICE_FLASH_SIZE_KB] = settings.FLASH['size']

    discover_device_net_config()
    discover_host_net_config()


def discover_device_net_config():
    if DEVICE_IP_ADDRESS in _attributes:
        return

    # lookup the IP address in the ARP cache
    cmd = 'arp -n -i {interface} | tail -n1 | grep -v incomplete | tr -s " " | cut -d " " -f 1,3'
    cmd = cmd.format(interface=settings.WIFI_INTERFACE)

    output = subprocess.check_output(cmd, shell=True).strip().decode()
    if output.startswith('arp:'):  # message when no entry found
        output = None

    if output:
        ip_address, mac_address = output.split()
        logger.debug('found device IP address in ARP cache: %s', ip_address)
        logger.debug('found device MAC address in ARP cache: %s', mac_address)
        _attributes[DEVICE_IP_ADDRESS] = ip_address
        _attributes[DEVICE_MAC_ADDRESS] = mac_address
        _attributes[DEVICE_MAC_ADDRESS_UPPER] = mac_address.upper()


def discover_host_net_config():
    cmd = 'ip addr show dev {interface}'.format(interface=settings.WIFI_INTERFACE)
    output = subprocess.check_output(cmd, shell=True).strip().decode()

    # MAC address
    if HOST_MAC_ADDRESS not in _attributes:
        result = re.findall(r'ether ([a-f0-9:]{17})', output)
        if result:
            logger.debug('found host MAC address: %s', result[0])
            _attributes[HOST_MAC_ADDRESS] = result[0]
            _attributes[HOST_MAC_ADDRESS_UPPER] = result[0].upper()

    # IP address & mask
    if HOST_IP_ADDRESS not in _attributes:
        result = re.findall(r'inet ([0-9.]{7,15})', output)
        if result:
            logger.debug('found host IP address: %s', result[0])
            _attributes[HOST_IP_ADDRESS] = result[0]

        result = re.findall(r'inet [0-9.]{7,15}/(\d+)', output)
        if result:
            logger.debug('found host IP mask: %s', result[0])
            _attributes[HOST_IP_MASK_CIDR] = int(result[0])
