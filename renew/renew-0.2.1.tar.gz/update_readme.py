#!/usr/bin/env python

# It's insane that pypi does not show README in markdown format while gitlab does not work wit restructured text.
# For me - it's easier to write readme in markdown, so since rst is needed, let's translate it with pypandoc.
import os
import sys

import pypandoc

assert len(sys.argv) == 2, "Missing main project dir argument"
PROJECT_MAIN_DIR = sys.argv[1]
assert os.path.isdir(PROJECT_MAIN_DIR), "wrong main project dir argument value"


def in_main(filename):
    file_path = os.path.join(PROJECT_MAIN_DIR, filename)
    assert os.path.isfile(file_path), "File does not exist: {}".format(file_path)
    return file_path


translated_readme = pypandoc.convert_file(in_main("README.md"), "rst")
with open(in_main("README.rst"), "wt") as out_file:
    out_file.write(translated_readme)
