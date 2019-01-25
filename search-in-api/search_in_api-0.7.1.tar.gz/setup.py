#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'altgraph==0.15',
    'asn1crypto==0.24.0',
    'certifi==2018.1.18',
    'cffi==1.11.4',
    'chardet==3.0.4',
    'cryptography==2.3.1',
    'dis3==0.1.2',
    'enum34==1.1.6',
    'future==0.16.0',
    'idna==2.6',
    'ipaddress==1.0.19',
    'macholib==1.9',
    'pefile==2017.11.5',
    'pycparser==2.18',
    'PyInstaller==3.3.1',
    'pyOpenSSL==17.5.0',
    'requests>=2.20.0',
    'six==1.11.0',
    'urllib3>=1.23',
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Aidas Bendoraitis",
    author_email='aidasbend@yahoo.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Search in API is a script that allows you to search among multiple pages of an API endpoint.",
    entry_points={
        'console_scripts': [
            'search_in_api=search_in_api.search_in_api:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='search_in_api',
    name='search_in_api',
    packages=find_packages(include=['search_in_api']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/archatas/search_in_api',
    version='0.7.1',
    zip_safe=False,
)
