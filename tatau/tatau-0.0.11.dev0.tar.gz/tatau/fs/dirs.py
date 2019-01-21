"""Utils to work with dirs"""
from collections import Iterable
from glob import iglob
import os


def list_files(path: str) -> Iterable:
    """
    Recursive files only listing in a directory

    :param path: directory to list
    :return: generator to files listing
    """
    for item in iglob(os.path.join(path, "**"), recursive=True):
        if os.path.isfile(item):
            yield item
