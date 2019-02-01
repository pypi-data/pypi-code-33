#!/usr/bin/python

import sys
import os
from setuptools import setup

# Scripts
scripts = []

# Local hack
if len(sys.argv) == 2 and sys.argv[1] == '--list-scripts':
    print(' '.join(scripts))
    sys.exit(0)

# Allow us to build on readthedocs which doesn't have MPI
install_requires = ['h5py', 'sphinx_rtd_theme']
if 'READTHEDOCS' not in os.environ:
    install_requires += ['mpi4py']

name = 'anamnesis'
version = '1.0'
release = '1.0.1'

setup(
    name=name,

    version=release,

    description='Object serialisation to/from HDF5 and via MPI',

    # Author details
    author='Mark Hymers',
    author_email='mark.hymers@ynic.york.ac.uk',

    # Choose your license
    license='GPL-2+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='hdf5 mpi serialisation',

    packages=['anamnesis',
              'anamnesis.mpiimps',
              'anamnesis.test',
              'anamnesis.test.data',
              'anamnesis.tests'],

    package_data={
        'anamnesis.test.data': ['*.hdf5']
    },

    install_requires=install_requires,

    extras_require={
        'test': ['coverage'],
    },

    command_options={
            'build_sphinx': {
                'project': ('setup.py', name),
                'version': ('setup.py', name),
                'release': ('setup.py', name)}}

)
