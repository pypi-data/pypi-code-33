#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
OMEGAlpes installation script

:authors: B. DELINCHANT, S. HODENCQ, Y. MARECHAL, L. MORRIET,
          C. PAJOT, F. WURTZ
:license: Apache Software License 2.0
:version: 0.0.1
"""

from setuptools import setup, find_packages

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 0, 1)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------


setup(

    name='omegalpes',
    version=__version__,
    packages=["omegalpes",
              "omegalpes.energy",
              "omegalpes.energy.io",
              "omegalpes.energy.units",
              "omegalpes.general",
              "omegalpes.general.optimisation"
              ],
    author="B. DELINCHANT, S. HODENCQ, Y. MARECHAL, L. MORRIET, "
           "C. PAJOT, V. REINBOLD, F. WURTZ",
    author_email='omegalpes-users@groupes.renater.fr',
    description="OMEGAlpes is a linear energy systems modelling library",
    long_description=open('README.md').read(),
    install_requires=[
        "PuLP >= 1.6.8",
        "Matplotlib >= 2.2.2, <3.1",
        "Numpy >= 1.14.2, <1.16",
        "Pandas >= 0.22.0, <0.24"
    ],
    include_package_data=True,

    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],

)
