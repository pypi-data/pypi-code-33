from enum import Enum
from distutils.version import StrictVersion
from functools import total_ordering
import logging

from pydotfiles.utils.io import run_command

logger = logging.getLogger(__name__)


class Setting:

    def __init__(self, name, valid_version_range, command, enabled=True, description=None, check_command=None, expected_check_state=None, run_as_sudo=False, check_output=True):
        self.name = name
        self.enabled = enabled
        self.description = description
        self.valid_version_range = valid_version_range
        self.command = command
        self.check_command = check_command
        self.expected_check_state = expected_check_state
        self.run_as_sudo = run_as_sudo
        self.check_output = check_output

    def __str__(self):
        return f"Setting(name={self.name}, enabled={self.enabled}, description={self.description}, valid_version_range={self.valid_version_range}, command={self.command}, check_command={self.check_command}, expected_check_state={self.expected_check_state})"

    def should_run(self, current_version, sudo_password):
        if not self.enabled:
            return False

        if not self.valid_version_range.is_in_range(current_version):
            return False

        if self.check_command is None:
            return True

        current_status_check_result = run_command(self.check_command, self.run_as_sudo, sudo_password, check_output=self.check_output)

        if current_status_check_result != self.expected_check_state:
            logger.info(f"Setting: Expected value not found, running command now [action={self.name}, expected={self.expected_check_state}, found={current_status_check_result}, run_as_sudo={self.run_as_sudo}")

        return current_status_check_result != self.expected_check_state

    def run(self, sudo_password):
        run_command(self.command, self.run_as_sudo, sudo_password, check_output=self.check_output)


class VersionRange:

    def __init__(self, start=None, end=None):
        """
        A None start is taken to be the equivalent
        of "since the beginning of time"

        A None end is taken to be the equivalent of
        "currently supported"
        """

        if start is not None and not isinstance(start, StrictVersion) and not isinstance(start, MacVersion):
            raise ValueError(f"Unable to create a version range, passed in type for start was invalid [start={type(start)}], should have been a StrictVersion")

        if end is not None and not isinstance(end, StrictVersion) and not isinstance(start, MacVersion):
            raise ValueError(f"Unable to create a version range, passed in type for start was invalid [end={type(start)}], should have been a StrictVersion")

        self.start = start
        self.end = end

    def __str__(self):
        return f"VersionRange(start={self.start}, end={self.end})"

    def is_in_range(self, current_version):
        # Infinite range case
        if self.start is None and self.end is None:
            return True

        if self.start is None and self.end is not None:
            return current_version <= self.end

        if self.end is None and self.start is not None:
            return self.start <= current_version

        # For somebody who likes to keep their books clean
        return self.start <= current_version <= self.end


@total_ordering
class MacVersion(Enum):

    YOSEMITE = StrictVersion("10.10")

    EL_CAPITAN = StrictVersion("10.11")

    SIERRA = StrictVersion("10.12")

    HIGH_SIERRA = StrictVersion("10.13")

    MOJAVE = StrictVersion("10.14")

    @staticmethod
    def from_version(version):
        if version is None:
            raise ValueError("MacVersion: Can't identify none version number")

        if isinstance(version, str):
            version = StrictVersion(version)

        major_version = version.version[0]
        minor_version = version.version[1]

        truncated_version = StrictVersion(f"{major_version}.{minor_version}")
        return MacVersion(truncated_version)

    @staticmethod
    def from_name(name):
        if name is None:
            raise KeyError("MacVersion: Can't identify none version name")
        return MacVersion[name.upper()]

    def __lt__(self, other):
        return self.value < other.value
