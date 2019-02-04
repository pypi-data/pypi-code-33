#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = []
setup_requirements = ["pytest-runner"]
test_requirements = ["pytest"]

setup(
    author="Devon Klompmaker",
    author_email='devon.klompmaker@aofl.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python implementation of client protocol for Coeus C# remote integration tests.",
    install_requires=requirements,
    license="MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='coeus-test',
    name='coeus-test',
    packages=['coeus_test'],
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    url='https://github.com/AgeOfLearning/coeus-python-framework',
    version='0.1.13',
    zip_safe=False,
)