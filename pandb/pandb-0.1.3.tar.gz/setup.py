#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Patrick Michl
#
# This file is part of pandora, https://frootlab.github.io/pandora
#
#  pandora is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  pandora is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  pandora. If not, see <http://www.gnu.org/licenses/>.
#
"""Setuptools based installation."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import pathlib
import re
import setuptools

def install() -> None:
    """Setuptools based installation script."""

    #Get module variables from file 'pandb/__init__.py'
    text = pathlib.Path('./pandb/__init__.py').read_text()
    rekey = "__([a-zA-Z][a-zA-Z0-9_]*)__"
    reval = r"['\"]([^'\"]*)['\"]"
    pattern = f"^[ ]*{rekey}[ ]*=[ ]*{reval}"
    pkg_vars = {}
    for mo in re.finditer(pattern, text, re.M):
        pkg_vars[str(mo.group(1))] = str(mo.group(2))

    # Install package
    setuptools.setup(
        name='pandb',
        version=pkg_vars['version'],
        description='pandora database proxy',
        long_description=pathlib.Path('.', 'README.rst').read_text(),
        long_description_content_type='text/x-rst',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3',
    		'Programming Language :: Python :: 3.7',
            'Operating System :: OS Independent',
            'Topic :: Database :: Database Engines/Servers',
            'Topic :: Software Development :: Libraries :: Python Modules'],
        keywords=(
            'database '
            'database-proxy '
            'orm-framework '
            'data-warehouse '),
        url='https://frootlab.github.io/pandora',
        author=pkg_vars['author'],
        author_email=pkg_vars['email'],
        license=pkg_vars['license'],
        packages=setuptools.find_packages(exclude=['docs', 'tests']),
        package_dir={
            'pandb': 'pandb'},
        python_requires='>=3.7',
        install_requires=[
            'numpy>=1.15',
            'SQLAlchemy>=1.2.17',
            'flab-errors>=0.0.2',
            'flab-base>=0.1.17',
            'flab-io>=0.1.4']
    )

if __name__ == '__main__':
    install()
