# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = "0.0.1"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="clib",
    version=version,
    author="eatenbyagrue",
    author_email="iwaseatenbyagrue@gmail.com",
    description="A command line base to help build CLIs faster.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/iwaseatenbyagrue/clib",
    packages=find_packages(exclude="tests"),
    include_package_data=True,
    install_requires=[
        "click",
        "click-plugins",
    ],
    setup_requires=[u"pytest-runner"],
    tests_require=[u"pytest", u"pytest-pep8", u"pytest-cov"],
    entry_points="""
[console_scripts]
clib=clib.cli.core:main
    """
)
