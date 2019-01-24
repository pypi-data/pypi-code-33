#!/usr/bin/env python

from setuptools import (
        setup as install,
        find_packages,
        )

VERSION = '0.1.0'

install(
        name='davinci',
        packages=['davinci'],
        version=VERSION,
        description='Implementation of standard Deep Learning Experiments in PyTorch.',
        author='Seb Arnold',
        author_email='smr.arnold@gmail.com',
        url = 'https://github.com/seba-1511/davinci',
        download_url = 'https://github.com/seba-1511/davinci/archive/0.1.3.zip',
        license='License :: OSI Approved :: Apache Software License',
        classifiers=[],
        scripts=[]
)
