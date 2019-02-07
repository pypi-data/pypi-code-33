#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2012 Damien Hardy dhardy@figarocms.fr

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


__version__ = None
exec(open('thumbor_cassandra/_version.py').read())

setup(
    name="thumbor_cassandra",
    packages=["thumbor_cassandra"],
    version=__version__,
    description="Apache Cassandra loader for Thumbor",
    author="Guilherme Borges",
    author_email="illidam.lopes@gmail.com",
    keywords=["thumbor", "cassandra", "images"],
    license='MIT',
    url='https://github.com/glborges/thumbor-cassandra',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: Portuguese',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                 'Topic :: Multimedia :: Graphics :: Presentation'
                 ],
    package_dir={"thumbor_cassandra": "thumbor_cassandra"},
    install_requires=["thumbor", "cassandra-driver"],
    long_description=readme()
)
