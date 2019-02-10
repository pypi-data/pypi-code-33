#!/usr/bin/env python
# encoding: utf-8

import os
from setuptools import setup


setup(
    name         = 'django-fas',
    version      = '1.2.1',
    description  = 'Django auth backend for FAS (Fedora Accounts System)',
    author       = 'Jakub Dorňák',
    author_email = 'jdornak@redhat.com',
    license      = 'BSD',
    url          = 'https://github.com/misli/django-fas',
    packages     = ['fas'],
    classifiers  = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ],
)
