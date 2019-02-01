#!/usr/bin/env python
"""twitchvod setup script"""

import os
from setuptools import setup


CWD = os.path.abspath(os.path.dirname(__file__))
PACKAGES = ["twitchvod"]
REQUIRES = ["requests>=2.13.0,<=2.21.0"]

VER = {}
VER_PATH = os.path.join(CWD, "twitchvod", "__version__.py")

with open(VER_PATH, "r") as f:
    exec(f.read(), VER) # pylint: disable=exec-used

with open("HISTORY.md", "r") as f:
    HIST = f.read()

with open("README.md", "r") as f:
    README = f.read()

setup(
    name=VER["__title__"],
    version=VER["__version__"],
    description=VER["__description__"],
    long_description=README,
    long_description_content_type="text/markdown",
    author=VER["__author__"],
    author_email=VER["__author_email__"],
    url=VER["__url__"],
    packages=PACKAGES,
    package_dir={"twitchvod": "twitchvod"},
    data_files=[(".", ["LICENSE", "README.md", "HISTORY.md"])],
    license=VER["__license__"],
    python_requires=">=3.5.2",
    install_requires=REQUIRES,
    zip_safe=False
)
