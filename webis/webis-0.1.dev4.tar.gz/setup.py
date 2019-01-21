#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os.path
import setuptools


with open("README.md") as f:
    longDescription = f.read()

with open("requirements.txt") as f:
    requirements = f.read()

# try to derive version from git tag,
# otherwise read from file VERSION
try:
    import git

    try:
        with git.Repo(".") as repo:
            version = repo.git.describe()
            with open("VERSION", "w") as f:
                f.write("{}\n".format(version))

    except git.exc.InvalidGitRepositoryError:
        raise RuntimeError("Not in git repository")

except (ImportError, RuntimeError, git.exc.GitCommandError):
    with open("VERSION") as f:
        version = f.read()
        # strip trailing newline
        version = version[:-1]

# strip initial "v"
version = version[1:]

packageName = setuptools.find_packages()[0]

setuptools.setup(
    name=packageName,
    version=version,
    author="Christoph Fink",
    author_email="christoph.fink@helsinki.fi",
    description="Python wrapper for the webis " +
    "Twitter sentiment identification tool",
    long_description=longDescription,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/christoph.fink/python-webis",
    packages=[packageName],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent"
    ],
    license="GPLv2"
)
