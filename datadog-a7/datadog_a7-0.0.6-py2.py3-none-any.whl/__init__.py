# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import json
import os
import six
import sys

from .validate import validate_py3


def main():
    """Run validate on a single python file"""
    if len(sys.argv) != 2:
        sys.stderr.write("No python file specified.\n")
        sys.stderr.flush()
        sys.exit(1)

    if isinstance(sys.argv[1], six.text_type):
        file_path = sys.argv[1]
    else:
        file_path = sys.argv[1].decode(sys.getfilesystemencoding())

    file_path = os.path.realpath(file_path)
    if not os.path.exists(file_path):
        sys.stderr.write(u"{} does not exist.\n".format(file_path))
        sys.stderr.flush()
        sys.exit(1)

    results = validate_py3(file_path)
    if results:
        print(json.dumps(results))
    else:
        print('[]')
