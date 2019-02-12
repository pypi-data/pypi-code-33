import os

import osascript

from mkalias_cli import strings


class Path:

    @staticmethod
    def check_path(path) -> bool:
        """
        Check if file or directory path is valid
        :param path: path to check
        :return: true if path exists otherwise returns false
        """

        if os.path.exists(path):
            return True
        else:
            print(strings.PATH_NOT_FOUND.format(path))
            return False


class Alias:
    #  Constants used for this Class
    CMD_STRING = 0
    CODE = 1
    OUT = 2
    ERROR = 3

    @staticmethod
    def create_alias(source, destination, name=None) -> tuple:
        """
        Creates and runs the AppleScript required to create the alias
        :param source: File or Directory to create an alias of
        :param destination: Destination directory of the new alias
        :param name: Name of new alias - OPTIONAL
        :return: tuple containing the AppleScript Created, Code, Output of AppleScript, and Errors - in that order
        """

        #  TODO: Update AppleScript to maybe not be one single command outlined below
        # cmd_string = 'tell application "Finder" \
        #     set mySource to POSIX file "{}" as alias \
        #     make new alias to mySource at POSIX file {} \
        #     set name of result to "{}" \
        #     end tell'.format(source, destination, name)
        if name is None:
            cmd_string = 'tell application "Finder" to make alias file to POSIX file "{}" at POSIX file "{}"' \
                .format(source, destination)
        else:
            cmd_string = 'tell application "Finder" \n \
            set mySource to POSIX file "{}" as alias \n \
            make new alias to mySource at POSIX file {} \n \
            set name of result to "{}" \n \
            end tell'.format(source, destination, name)

        code, out, error = osascript.run(cmd_string)

        return cmd_string, code, out, error

    @staticmethod
    def rename_alias(source, destination, name):
        """
        Rename the new alias to a custom name instead of "example alias"

        :param name: custom name of new alias
        :param source: Name of the source file/dir for the alias
        :param destination: destination for the alias
        :return: none
        """

        #  TODO: multiple aliases create result in a number being added to each new alias, alias 2, alias 3, etc
        #       we need to deal with this somehow
        source_head, source_tail = os.path.split(source)

        alias_name = source_tail + " alias"
        alias_path = destination + "/" + alias_name
        new_name_path = destination + "/" + name

        os.rename(alias_path, new_name_path)
        print(new_name_path)
