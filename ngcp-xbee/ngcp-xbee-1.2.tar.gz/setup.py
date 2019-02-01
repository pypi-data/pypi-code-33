# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2017, 2018, Digi International Inc. All Rights Reserved.

from setuptools import setup, find_packages
from codecs import open
from os import path


DEPENDENCIES = (
    'pyserial>=3',
    'ipaddress>=1',
    'enum34>=1'
)

here = path.abspath(path.dirname(__file__))
 
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
 
setup(
    name='ngcp-xbee',
    version='1.2',
    description='Digi XBee Python library, compatible with Python 2',
    long_description=long_description,
    url='https://github.com/tianatonnu/python-xbee.git',
    author='Tiana Ton Nu, Digi International Inc.',
    author_email='tianattonnu@gmail.com, tech.support@digi.com',
    packages=find_packages(exclude=('unit_test*', 'functional_tests*', 'demos*')),
    keywords=['xbee', 'IOT', 'wireless', 'radio frequency'],
    license='Mozilla Public License 2.0 (MPL 2.0)',
    python_requires='>=2',
    install_requires=[
        'pyserial>=3',
        'ipaddress>=1',
        'enum34>=1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Libraries',
        'Topic :: Home Automation',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
    ],
)
