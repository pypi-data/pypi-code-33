#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
from rokit.__version__ import __version__

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

setup(
    name="rokit",
    packages=find_packages(),
    version=__version__,
    description="Redirection Optimization Kit",
    author="wizardbyron",
    author_email="wizardbyon@icloud.com",
    url="https://github.com/wizardbyron/rokit",
    keywords=["url", "redirection", "redirect", "verify", "test", "tests"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities"
    ],
    include_package_data=True,
    install_requires=['requests', 'click', 'future'],
    entry_points={
        'console_scripts': [
            'rokit = rokit:cli'
        ]
    },
    python_requires='>=2.6, >=3.6, <4',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
