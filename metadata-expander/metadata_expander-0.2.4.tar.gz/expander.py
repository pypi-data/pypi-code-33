#!/usr/bin/env python3
"""
Entrypoint for CLI execution, parses given arguments.

Arguments:
doi: DOI of the document
-s: Search string, e.g. a title
"""
import argparse
import sys
from sys import argv

from metadata_expander import search_doi, search_string
from metadata_expander.custom_exceptions import DocumentNotFound


def check_version():
    """
    Check the python version.

    Required: Python3, Recommended: Python 3.6 or higher
    """
    version = sys.version_info[0]
    if version < 3:
        version = "{}.{}".format(sys.version_info[0], sys.version_info[1])
        print("You are running Python", version)
        print("Required: Python 3")
        print("Recommended: Python 3.6")
        return False
    return True


def main():
    """
    Main.

    Parse cl and search for metadata by doi or search term
    """
    parser = argparse.ArgumentParser(prog="python3 metadata_expander")
    parser.add_argument("doi", nargs='?', help="DOI of the document")
    parser.add_argument("-s", "--string",
                        help="Information about the document, e.g. title")
    args = parser.parse_args()

    if not check_version():
        return None

    if len(argv) == 1:
        parser.print_help(sys.stderr)
    else:
        if args.doi is not None:
            result = search_doi(str(args.doi))
            print(result)
            return result
        try:
            result = search_string(args.string)
            print(result)
            return result
        except DocumentNotFound:
            print("No matching document was found.")
    return None


if __name__ == '__main__':
    main()
