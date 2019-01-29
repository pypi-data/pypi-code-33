#!/usr/bin/env python

from setuptools import setup

setup(
    name='samtal',
    version="0.0.5",
    description='Simple assessment bot',
    long_description='Simple assessment bot',

    # The project's main homepage.d
    url='https://gitlab.com/azae/outils/samtal/',

    # Author details
    author='Alexis Benoist, Thomas Clavier, Benoit Maurice',

    # Choose your license
    license='GPL 3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='bot',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['samtal', 'samtal/core','samtal/adapters'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'PyYAML',
        'mattermostdriver',
        'textblob',
        'pony',
        'dataclasses',
    ],
)
