#!/usr/bin/env python
#
# Copyright (C) 2017 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
# pylint: disable=bad-whitespace

from setuptools import setup

# Grab description for Pypi
with open('README.md') as fhl:
    DESC = fhl.read()

setup(
    name             = "cmsplugin-alerts",
    version          = "1.2.1",
    description      = "Extend django-cms with emails when pages are published.",
    long_description = DESC,
    author           = 'Martin Owens',
    url              = 'https://gitlab.com/doctormo/django-cmsplugin-alerts',
    author_email     = 'doctormo@gmail.com',
    platforms        = 'linux',
    license          = 'LGPLv3',
    packages         = ['cmsplugin_alerts'],
    include_package_data=True,
    package_dir={
        'cmsplugin_alerts': 'cmsplugin_alerts',
    },
    install_requires = ['django-cms>=3.5', 'django-boxed-alerts>=1.3.4'],
    classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
