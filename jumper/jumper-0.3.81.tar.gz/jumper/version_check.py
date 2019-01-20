import os
from distutils.version import LooseVersion
from __version__ import __version__
import requests
from termcolor import colored
from terminaltables import AsciiTable
from terminaltables import SingleTable

DOCKER_JUMPER_VLAB_MESSAGE = "jumperio/jumper-vlab"
DOCKER_VLAB__GCC_ARM_MESSAGE = "jumperio/vlab-gcc-arm"


def _get_latest_version(name):
    url = "https://pypi.python.org/pypi/{}/json".format(name)
    try:
        return list(reversed(sorted(requests.get(url).json()["releases"], key=LooseVersion)))[0]
    except Exception as e:
        return None


def check_sdk_version(local_jemu):
    if not local_jemu:
        jumper_latest_version = _get_latest_version("jumper")
        if jumper_latest_version:
            if LooseVersion(__version__) < LooseVersion(jumper_latest_version):
                _print_update_to_screen(jumper_latest_version)


def _get_update_message_for_docker(jumper_latest_version, docker_name):
    update_message = "Update available {0} ".format(__version__) + u'\u2192' + colored(
        " " + jumper_latest_version, 'green', attrs=['bold'])
    how_to_updtae_message = "\n  You can either run: " + colored("pip install jumper --upgrade ", "blue",
        attrs=['bold']) + "to update" + "\n  or exit docker and pull this container: " + colored(
        "docker pull " + docker_name + " ", "blue", attrs=['bold'])
    return update_message + how_to_updtae_message


def _get_update_message(jumper_latest_version):
    if os.name == 'nt':
        update_message = "Update available from {0}".format(__version__) + " to " + jumper_latest_version
        how_to_update_message = "\n  Run pip install jumper --upgrade to update"
    else:
        update_message = "Update available {0} ".format(__version__) + u'\u2192' + colored(
            " " + jumper_latest_version, 'green', attrs=['bold'])
        how_to_update_message = "\n  Run " + colored(" sudo pip install jumper --upgrade ", "blue",
                                                     attrs=['bold']) + "to update"
    return update_message + how_to_update_message


def _print_update_to_screen(jumper_latest_version):
    if 'DOCKER_JUMPER' in os.environ:
        message = _get_update_message_for_docker(jumper_latest_version, DOCKER_JUMPER_VLAB_MESSAGE)
    elif 'DOCKER_JUMPER_EXAMPLES' in os.environ:
        message = _get_update_message_for_docker(jumper_latest_version, DOCKER_VLAB__GCC_ARM_MESSAGE)
    else:
        message = _get_update_message(jumper_latest_version)

    print("\n")
    table_data = [[message]]
    if os.name == 'nt':
        table = AsciiTable(table_data)
    else:
        table = SingleTable(table_data)
    table.padding_left = 2
    table.padding_right = 2
    print(table.table.encode('utf-8'))
