#   Setup procedures for greenland4.
#   Copyright (C) 2018 M E Leypold
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <https://www.gnu.org/licenses/>.
#

import setuptools
import datetime

with open("README.rst", "r") as fh:
    long_description = fh.read()

exclude = ['test','tests','example','examples','demo','demos']
def is_excluded(p):
    for suffix in exclude:
        if p[-len(suffix)-1:] == "."+suffix: return True
    return False

packages = [ package for package in setuptools.find_packages("lib") if not is_excluded(package) ]

loc_suffix = "+T"+datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d%H%M%S")

setuptools.setup(
    name="greenland",
    version="0.0.5", # + loc_suffix,
    author="Markus E Leypold",
    author_email="greenland-4sda212@m-e-leypold.de",
    description="A pythonic scripting environment",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/m-e-leypold/greenland4",
    packages=packages,
    package_dir={ '': 'lib' },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
