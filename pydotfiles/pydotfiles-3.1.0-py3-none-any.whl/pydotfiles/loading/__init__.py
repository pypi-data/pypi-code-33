import plistlib
from typing import Dict, List
from pydotfiles.models.utils import load_data_from_file
from pydotfiles.defaults import MacVersion, VersionRange, Setting

from pydotfiles.environments import VirtualEnvironment
from pydotfiles.environments import LanguagePluginManager, LanguageEnvironmentPluginManager
from pydotfiles.environments import LanguageManager, LanguageEnvironmentManager
from pydotfiles.environments import DevelopmentEnvironment


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

    version = default_settings_data.get("version")
    schema_type = default_settings_data.get("schema")

    if version != "alpha":
        raise NotImplementedError(f"Loading: Unable to load default settings file with an unsupported version number [found_version={version}]")

    if schema_type != "default_settings":
        raise ValueError(f"Loading: Invalid data file was passed in based on detected schema type [schema_type={schema_type}]")

    return alpha_default_parse_data(default_settings_data.get("default_settings"))


def parse_developer_environments(developer_environments_data):
    if developer_environments_data is None:
        return []

    return alpha_developer_environments_parse_data(developer_environments_data)


"""
Version-based parsers
"""


def alpha_default_parse_data(default_settings_data):
    settings = []
    for raw_setting in default_settings_data:
        name = raw_setting.get("name")
        enabled = raw_setting.get("enabled", True)
        description = raw_setting.get("description")

        raw_start = raw_setting.get("start")
        start = None if raw_start is None else MacVersion.from_name(raw_start)

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


def alpha_developer_environments_parse_data(developer_environments_data):
    developer_environments = []

    for raw_developer_environment in developer_environments_data:
        language = raw_developer_environment.get("language")
        versions = raw_developer_environment.get("versions")
        language_environment_manager = parse_language_environment_manager(raw_developer_environment.get("environment_manager"))

        developer_environments.append(DevelopmentEnvironment(
            language=language,
            versions=versions,
            language_environment_manager=language_environment_manager
        ))
    return developer_environments


def parse_language_environment_manager(environment_manager_data: Dict):
    environment_manager = LanguageManager.from_string(environment_manager_data.get("name"))
    plugin_managers = parse_language_environment_plugins(environment_manager_data.get("plugins"))

    return LanguageEnvironmentManager(environment_manager, language_plugin_managers=plugin_managers)


def parse_language_environment_plugins(plugins_data: List[Dict]):
    if plugins_data is None:
        return []

    plugin_managers = []
    for plugin_data in plugins_data:
        language_plugin = LanguagePluginManager.from_string(plugin_data.get("name"))
        virtual_environments_data = parse_virtual_environments(plugin_data.get("virtual_environments"))
        plugin_managers.append(LanguageEnvironmentPluginManager(language_plugin, virtual_environments_data))
    return plugin_managers


def parse_virtual_environments(virtual_environments_data: List[Dict]):
    if virtual_environments_data is None:
        return []
    return [VirtualEnvironment(virtual_environment.get("version"), virtual_environment.get("name")) for virtual_environment in virtual_environments_data]
