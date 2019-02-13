#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["numpy",
                  "scipy",
                  "plasmapy",
                  "numba",
                  ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]


setup(
    author="Antoine Tavant",
    author_email='antoinetavant@hotmail.fr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Solve the stationnary collisionless plasma sheath model using polytropic law as electr energy equation closure",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sheath_fluid',
    name='sheath_fluid',
    packages=find_packages(include=['sheath_fluid']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/antoinelpp/sheath_fluid',
    download_url="https://github.com/antoinelpp/sheath_fluid/archive/0.2.tar.gz",
    version='0.2.0',
    zip_safe=False,
)
