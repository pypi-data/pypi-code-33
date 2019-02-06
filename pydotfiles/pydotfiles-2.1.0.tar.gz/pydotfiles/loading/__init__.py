import plistlib

from pydotfiles.models.utils import load_data_from_file
from pydotfiles.defaults import MacVersion, VersionRange, Setting


def get_os_default_settings(default_setting_file_path):
    # Loads in the default settings file
    default_settings_data = load_data_from_file(default_setting_file_path)

    # Parses the default settings data
    return parse_default_settings(default_settings_data)


"""
Loading methods
"""


def load_plist(plist_path):
    with open(plist_path, 'rb') as plist_file:
        return plistlib.load(plist_file)


"""
Parsing methods
"""


def parse_default_settings(default_settings_data):
    if not default_settings_data:
        default_settings_data = []

    settings = []
    for raw_setting in default_settings_data:
        name = raw_setting.get("name")
        enabled = raw_setting.get("enabled", True)
        description = raw_setting.get("description")
        start = MacVersion.from_name(raw_setting.get("start"))

        raw_end = raw_setting.get("end")
        end = None if raw_end is None else MacVersion.from_name(raw_end)

        valid_version_range = VersionRange(start, end)
        command = raw_setting.get("command")
        check_command = raw_setting.get("check_command")
        expected_check_state = raw_setting.get("expected_check_state")

        run_as_sudo = raw_setting.get("sudo", False)

        check_output = raw_setting.get("check_output", True)
        settings.append(Setting(
            name=name,
            valid_version_range=valid_version_range,
            command=command,
            enabled=enabled,
            description=description,
            check_command=check_command,
            expected_check_state=expected_check_state,
            run_as_sudo=run_as_sudo,
            check_output=check_output,
        ))

    return settings
