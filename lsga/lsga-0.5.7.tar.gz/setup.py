#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from lsga import __version__ as version

maintainer = 'Marko Stojanovic'
maintainer_email = 'marko.stojanovickg@outlook.com  '
author = maintainer
author_email = maintainer_email
description = "A Genetic Algorithm Framework in Python"
long_description = '''
====
LSGA Package
====


'''

install_requires = [
]

license = 'LICENSE'

name = 'lsga'
platforms = ['linux', 'windows', 'macos']
url = 'https://github.com/mstojanovickg/lsga'
download_url = 'https://github.com/mstojanovickg/lsga/releases'

classifiers = [
    'Development Status :: 3 - Alpha',
    'Topic :: Utilities',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
]

test_suite = 'lsga.tests.test_all'

setup(
    author=author,
    author_email=author_email,
    description=description,
    license=license,
    long_description=long_description,
    install_requires=install_requires,
    maintainer=maintainer,
    name=name,
    packages=find_packages(),
    platforms=platforms,
    url=url,
    download_url=download_url,
    version=version,
    test_suite=test_suite
)

