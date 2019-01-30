#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='unicmobile_common',
    version='1.0',
    description='UnicMobile common package',
    author='Omar Diaz',
    author_email='oadiaz@unicmobile.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
      'dependency_injector',
      'requests',
    ],
    zip_safe=False,
)
