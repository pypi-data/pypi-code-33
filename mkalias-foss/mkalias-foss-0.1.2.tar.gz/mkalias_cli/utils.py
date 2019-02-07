import os

import osascript
import strings


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
    def create_alias(source, destination) -> tuple:
        """
        Creates and runs the AppleScript required to create the alias
        :param source: File or Directory to create an alias of
        :param destination: Destination directory of the new alias
        :return: tuple containing the AppleScript Created, Code, Output of AppleScript, and Errors - in that order
        """

        cmd_string = 'tell application "Finder" to make alias file to POSIX file "{}" at POSIX file "{}"' \
            .format(source, destination)

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

        source_head, source_tail = os.path.split(source)

        alias_name = source_tail + " alias"
        alias_path = destination + "/" + alias_name
        new_name_path = destination + "/" + name

        os.rename(alias_path, new_name_path)
        print(new_name_path)
