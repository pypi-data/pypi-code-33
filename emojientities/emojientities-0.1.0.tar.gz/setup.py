#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

setuptools.setup(
    name="emojientities",
    version=version,
    author="Christoph Fink",
    author_email="christoph.fink@helsinki.fi",
    description="provides `string.emojis` (all emoji characters from unicode.org)",
    long_description=longDescription,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/christoph.fink/python-emojientities",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent"
    ],
    license="GPLv2" # ,
    # entry_points={
    #     "console_scripts": [
    #         "smdd = SocialMediaDataDownloader:main_func"
    #     ]
    # }
)
