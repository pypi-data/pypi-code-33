# Copyright (c) 2019 bluelief.
# This source code is licensed under the MIT license.

import fnmatch
import sys
import os
from distutils import dir_util


ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project")


def create_files(package_name):
    """ Create init files """
    try:
        if package_name is None:
            dir_util.copy_tree(ASSET_DIR, os.path.abspath("."))
        else:
            dir_util.copy_tree(
                ASSET_DIR, os.path.join(os.path.abspath("."), package_name)
            )
    except Exception as e:
        print(e)
    else:
        current_name = os.path.join(
            os.path.join(os.path.abspath("."), package_name), "project"
        )
        new_name = os.path.join(
            os.path.join(os.path.abspath("."), package_name), package_name
        )
        os.rename(current_name, new_name)
        print("[x] Compleate create files.")


def insert_strings(package_name, author_name):
    files = []
    for root, dirnames, filenames in os.walk(package_name):
        for filename in filenames:
            if not fnmatch.fnmatch(filename, "*.pyc"):
                files.append(os.path.join(root, filename))
    print("[x] Found {0} files".format(len(files)))
    print(files)

    try:
        with open("HEADER", "r") as file:
            source_header = file.read()
    except EnvironmentError:
        print("[x] Can't open HEADER file. (e.g. touch HEAD && vim HEAD)")
        exit()

    for editfile in files:
        with open(editfile, "r") as file:
            filedata = file.read()

        filedata = filedata.replace("PACKAGENAME", package_name)
        filedata = filedata.replace("AUTHORNAME", author_name)
        filedata = filedata.replace("SOURCEHEADER", source_header)

        with open(editfile, "w") as file:
            file.write(filedata)
    print("[x] Compleate edit files.")


def main():
    package_name = input("[x] What is your project name? (package) > ")
    author_name = input("[x] What is your name? (author) > ")

    create_files(package_name)
    insert_strings(package_name, author_name)


if __name__ == "__main__":
    main()
