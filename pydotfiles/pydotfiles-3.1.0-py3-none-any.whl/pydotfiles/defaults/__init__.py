import platform
from .primitives import MacVersion, VersionRange, Setting


def get_current_mac_version():
    current_version = platform.mac_ver()[0]
    return MacVersion.from_version(current_version)
