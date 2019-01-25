"""setup.py"""
# -*- coding: utf-8 -*-
#/usr/bin/env python

from setuptools import setup, find_packages

LONG_DESCRIPTION = open('intro.rst', 'r').read()

INSTALL_REQUIRES = [
    'Django',
    'pillow'
]

setup(
    name='django-simditor2',
    version='0.1',
    packages=find_packages(exclude=[".DS_Store"]),
    include_package_data=True,
    license='MIT License',
    description='A Django admin Simditor integration.',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/sai628/django-simditor2',
    author='Sai628',
    author_email='sai100628@gmail.com',
    keywords='Django admin Simditor integration',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=INSTALL_REQUIRES,
)
