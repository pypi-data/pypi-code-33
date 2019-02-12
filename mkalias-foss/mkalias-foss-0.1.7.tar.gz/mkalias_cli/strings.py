"""
This file is purely for String resources, and must NEVER contain any code
"""


class Parser:
    HELP_SOURCE = "Source to create alias from"
    HELP_DESTINATION = "Destination directory of alias"
    HELP_ALIAS_NAME = "Set the name of the new alias"
    HELP_VERSION = "Display version info"


class Errors:
    PATH_NOT_FOUND = "'{} not found!"
    PATH_IS_LINK = "'{}' is a symbolic link"
