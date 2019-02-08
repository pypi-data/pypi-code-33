#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages
from django_saml2_framework import __version__
try:
    from pypandoc import convert_file as convert
except ImportError:
    import io
    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()
DESCRIPTION = 'A framework for using SAML2 with Django.'
CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]
setup(
    name='django-saml2-framework',
    version=__version__,
    author='Kevin Clark',
    # author_email='kevin@example.com',
    description=DESCRIPTION,
    long_description=convert('README.md', 'rst'),
    url='https://gitlab.com/hybridlogic/django-saml2-framework/',
    license='Apache Software License',
    keywords=['django','sso', 'saml', 'saml2'],
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['example', 'docs']),
    include_package_data=True,
)
