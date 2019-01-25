#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from djcms_blog import __version__

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = [
    "django-simplemde==0.1.2",
    "dj_markdown==0.1.2",
    "Pillow==5.4.1",
    "django"
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Carlos Martinez",
    author_email="me@carlosmart.co",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    description="Simple Django Blog app using Markdown",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="djcms_blog",
    name="djcms_blog",
    packages=find_packages(include=["djcms_blog"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/carlosmart626/djcms_blog",
    version=__version__,
    zip_safe=False,
)
