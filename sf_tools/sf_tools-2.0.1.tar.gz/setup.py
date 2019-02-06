#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

release_info = {}
infopath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                           "sf_tools", "info.py"))
with open(infopath) as open_file:
    exec(open_file.read(), release_info)

setup(
    name='sf_tools',
    author='sfarrens',
    author_email='samuel.farrens@cea.fr',
    version=release_info["__version__"],
    url='https://github.com/sfarrens/sf_tools',
    download_url='https://github.com/sfarrens/sf_tools',
    packages=find_packages(),
    install_requires=['numpy>=1.14.1', 'future>=0.16.0', 'modopt>=1.1.4'],
    license='MIT',
    description='Tools for image analysis, signal processing and statistics.',
    long_description=release_info["__about__"],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', 'pytest-cov', ],
)
