# Copyright 2019 Philip Starkey
#
# This file is part of iradon.

import os
from setuptools import setup, find_packages

# Define the current version of the library
# Update this before building and publishing a new version
# see https://semver.org/ for guidelines on how to modify the version string
VERSION = '1.0.1'

# get directory of setup.py and the rest of the code for the library
code_dir = os.path.abspath(os.path.dirname(__file__))

# Auto generate a __version__ file for the package to import
with open(os.path.join(code_dir, 'piradon', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n" % VERSION)

# Work around the fact that the readme.md file doesn't exist for users installing
# from the tar.gz format. However, in this case, they won't be uploading to PyPi
# so they don't need it!
try:
    # Read in the readme file as the long description
    with open(os.path.join(code_dir, 'readme.md')) as f:
        long_description = f.read()
except Exception:
    long_description = ""

setup(
    name='piradon',
    version=VERSION,
    description='A fork of the skimage iradon function, modified so that the output matches results from MATLAB',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://piradon.readthedocs.io',
    project_urls={
        "Documentation": "https://piradon.readthedocs.io",
        "Source Code": "https://bitbucket.org/philipstarkey/piradon",
    },
    license='Modified BSD',
    author='Philip Starkey',
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Environment :: Console',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering',
                ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy>=1.11',
        'scipy>=0.17.0',
    ],
)