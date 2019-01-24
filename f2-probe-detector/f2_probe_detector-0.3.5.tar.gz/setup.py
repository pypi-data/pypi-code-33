#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(

    name='f2_probe_detector',
    version_format='{tag}.{commitcount}',
    description='Flamingos 2 - Probe Detector',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Bruno Quint',
    author_email="bquint@gemini.edu",
    url='https://gitlab.gemini.edu/DRSoftware/gemaux_python/',
    packages=[
        'f2_probe_detector',
    ],

    setup_requires=[
        # "pytest-runner",  # Why do we need pytest-runner?
        "setuptools-git-version",
    ],

    test_requires=[
        "pytest",
    ],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    scripts=[
        './f2_probe_detector/scripts/get_f2_probe_position',
    ],

)
