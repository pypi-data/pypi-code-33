#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import pyprimed

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "requests==2.18.4",
    "pytz==2017.3",
    "daiquiri==1.3.0",
    "tqdm==4.23.0",
    "pandas>=0.22.0"
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name="pyprimed",
    version=pyprimed.__version__,
    description="Python client to manage PrimedIO",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Matthijs van der Kroon",
    author_email="matthijs@primed.io",
    url="https://gitlab.com/primedio/delivery-pyprimed",
    packages=find_packages(),
    package_dir={"pyprimed": "pyprimed"},
    entry_points={},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="pyprimed primedio",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
