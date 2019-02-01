#!/usr/bin/env python

# Copyright (c) 2019 CANDY LINE INC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    try:
        with open('README.md', 'r') as f:
            long_description = f.read()
    except IOError:  # For tox
        long_description = ""

version = "3.2.0"

if sys.argv[-1] == 'publish':
    os.system('rm -fr dist/*')
    os.system('python setup.py sdist')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name='candy-board-cli',
    version=version,
    author='Daisuke Baba',
    author_email='baba.daisuke@gmail.com',
    url='http://github.com/CANDY-LINE/candy-board-cli',
    download_url='https://github.com/CANDY-LINE/candy-board-cli/tarball/{0}'
        .format(version),
    description='CANDY Board Service CLI',
    long_description=long_description,
    license='ASL 2.0',
    scripts=['bin/candy'],
    classifiers=[
                    'Programming Language :: Python',
                    'Development Status :: 5 - Production/Stable',
                    'Natural Language :: English',
                    'Environment :: Console',
                    'Intended Audience :: System Administrators',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: Apache Software License',
                    'Operating System :: POSIX :: Linux',
                    'Topic :: System :: Hardware',
                ],
    keywords=(
        'CANDY RED',
        'CANDY EGG',
        'CANDY LINE',
        'CANDY Pi Lite',
        'CANDY Pi Lite+'
        ),
)
