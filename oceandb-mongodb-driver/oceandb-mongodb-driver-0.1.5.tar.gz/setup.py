#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md', encoding='utf-8') as changelog_file:
    changelog = changelog_file.read()

requirements = ['oceandb-driver-interface', 'pymongo', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="leucothia",
    author_email='devops@oceanprotocol.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="🐳 Mongo DB BigchainDB driver (Python).",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='oceandb-mongodb-driver',
    name='oceandb-mongodb-driver',
    packages=find_packages(include=['oceandb_mongodb_driver']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/oceanprotocol/oceandb-mongodb-driver',
    version='0.1.5',
    zip_safe=False,
)
