#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Time    : 2018/10/16 17:37
# Author  : gaojiewen
# Version : 1.0
# Desc    :

import os
import io
from setuptools import find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'eadb', '__about__.py'), encoding='utf-8') as f:
    exec(f.read(), about)


print(about)
setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    python_requires='>=3.0, <4',
    packages=find_packages(exclude=["examples", "tests", "tests.*"]),
    install_requires=[],

)
