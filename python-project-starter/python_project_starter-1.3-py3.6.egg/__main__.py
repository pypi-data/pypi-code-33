#!/usr/bin/python
"""
    python-project-starter: easy package creator
"""
import argparse
import shutil
import os


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='python-project-starter by Henri Devigne')

    parser.add_argument('path',
                        action="store",
                        type=str,
                        help="Path where the project will be create",
                        default=".")
    parser.add_argument('-n', '--name',
                        action="store",
                        type=str,
                        help="Name of the project",
                        default=None)
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="Enable verbosity",
                        default=False)

    arguments = parser.parse_args()

    try:
        # see https://github.com/PyCQA/pylint/issues/2696
        # pylint: disable=C0321
        if arguments.verbose: print("Cloning template into: " + arguments.path)
        shutil.copytree(
            src=os.path.dirname(os.path.realpath(__file__)) + "/template",
            dst=arguments.path,
            ignore=shutil.ignore_patterns("*.pyc")
        )
    except OSError:
        print("Unable to create project in: " + arguments.path)
        return -1

    module_directory_name = arguments.name if arguments.name else os.path.basename(arguments.path)
    module_path = arguments.path + "/" + module_directory_name

    os.rename(
        arguments.path + "/my_project",
        module_path
    )

    for directory, _, file_names in os.walk(arguments.path):
        for file_name in file_names:
            replace_in_file(
                path=os.path.abspath(os.path.join(directory, file_name)),
                search="my_project",
                replace=module_directory_name
            )

    return 0


def replace_in_file(path, search, replace):
    """
    Replace a string per another in a file
    :param path: path of the file
    :type path: str
    :param search: string to replace
    :type search: str
    :param replace: replacement string
    :type replace: str
    :return: None
    """
    raw = open(path, "r")
    data = raw.read().replace(search, replace)
    raw.close()

    raw = open(path, 'w')
    raw.write(data)
    raw.close()


if __name__ == '__main__':
    main()
