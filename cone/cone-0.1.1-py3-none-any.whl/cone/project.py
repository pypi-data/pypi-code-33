import json
import os
import traceback

from cone.ConeExit import ConeExit


def validate_configuration(configuration, file_name):
    if type(configuration) != list:
        raise ConeExit.error(
            "Configuration file <{}> has to be a list".format(file_name))

    for index, config_entry in enumerate(configuration):
        path = config_entry.get("path", None)
        parent = config_entry.get("parent", None)

        if path is None:
            raise ConeExit.error("Error in cone configuration file: entry #{}".format(index) +
                                 " does not contain a <path> key (entry: {})".format(config_entry))
        if parent is None:
            raise ConeExit.error("Error in cone configuration file: entry #{}".format(index) +
                                 " does not contain a <parent> key (entry: {})".format(config_entry))

        if not os.path.exists(path):
            raise ConeExit.error(
                "Error in cone configuration file: path '{}' does not exist".format(path))


def get_configuration(file_name="cone.json"):
    current_path = os.getcwd()
    config_path = os.path.join(current_path, file_name)

    if os.path.isfile(config_path):
        with open(config_path, "r") as config_file:
            configuration = json.load(config_file)
            validate_configuration(configuration, file_name)

            return configuration
    else:
        raise ConeExit.error(
            "Can not find configuration file <{}>".format(file_name))


def get_file_content(path):
    with open(path, "r") as f:
        return "".join(f.readlines())


def get_folder_content(path):
    project_data = {}

    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)

        if os.path.isdir(file_path):
            project_data[file_name] = get_folder_content(file_path)
        else:
            if file_name.endswith(".lua"):
                project_data[file_name] = get_file_content(file_path)

    return project_data


def filter_project_tests(project_data):
    removeKeys = []
    for name, content in project_data.items():
        if name.endswith(".spec.lua"):
            removeKeys.append(name)
        elif type(content) is dict:
            filter_project_tests(content)

    for key in removeKeys:
        del project_data[key]


def get_project_content(configuration):
    current_path = os.getcwd()
    project_data = get_folder_content(current_path)

    for config_entry in configuration:
        if "include_tests" in config_entry.keys():
            if not config_entry["include_tests"]:
                content = project_data

                path = os.path.normpath(config_entry["path"])
                if os.path.isfile(path):
                    path = os.path.dirname(path)

                for key in path.split(os.sep):
                    content = content[key]

                filter_project_tests(content)

    return project_data
