
#!/usr/bin/env python

"""Setup script for Robot's SCLibrary distributions"""

import re
from os.path import abspath, dirname, join
from setuptools import setup, find_packages

CURDIR = dirname(abspath(__file__))

with open(join(CURDIR, 'src', 'SCLibrary', '__init__.py')) as f:
    VERSION = re.search("\n__version__ = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'README.md')) as f:
    DESCRIPTION = f.read()
with open(join(CURDIR, 'requirements.txt')) as f:
    REQUIREMENTS = f.read().splitlines()

def main():
    setup(name             = 'rf-sclibrary',
          version          = VERSION,
          description      = 'SC utility library for Robot Framework',
          long_description = DESCRIPTION,
          author           = 'YoKey',
          author_email     = 'yokeyword@gmail.com',
          url              = 'https://github.com/',
          package_dir      = { '' : 'src'},
          packages         = find_packages('src'),
          install_requires = REQUIREMENTS
          )


if __name__ == "__main__":
    main()