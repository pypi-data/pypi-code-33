import platform
from enum import Enum, auto


class OS(Enum):
    """
    Represents a given operating system
    """
    MACOS = auto()
    LINUX = auto()
    UBUNTU = auto()
    CENTOS = auto()

    @staticmethod
    def get_host_system():
        host_system = platform.system().lower()

        if host_system == "darwin":
            return OS.MACOS
        else:
            raise NotImplementedError(f"OS: The host system's OS is not currently supported [os={host_system}]")

    @staticmethod
    def from_string(label):
        if label is None:
            raise KeyError("Enum: No operating system was passed in")

        if label == "darwin":
            return OS.MACOS

        return OS[label.upper()]

    @staticmethod
    def get_package_manager(os):
        return {
            OS.MACOS: PackageManager.BREW,
            OS.LINUX: PackageManager.APT,
            OS.UBUNTU: PackageManager.APT,
            OS.CENTOS: PackageManager.YUM
        }.get(os)


class PackageManager(Enum):
    """
    Represents a system package manager
    """
    BREW = auto()

    # Linux package managers
    YUM = auto()
    APT = auto()

    @staticmethod
    def from_label(label):
        if label is None:
            raise KeyError("Enum: No package manager was passed in")
        return PackageManager[label.upper()]
