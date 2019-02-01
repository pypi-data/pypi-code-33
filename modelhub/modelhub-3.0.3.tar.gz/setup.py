#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

try:
    README = open('README.md').read()
except Exception:
    README = ""
VERSION = "3.0.3"
TF_REQUIRE_VERSION = "1.4.0"

requirments = [
    "click",
    "boto3",
    "protobuf",
    "appdirs",
    "grpcio",
    "six",
    "genson",
    "jsonschema",
    "pipreqs-spenly",
    "jinja2",
    "numpy"
]

if sys.version_info.major < 3:
    requirments += ["configparser", "pathlib"]

setup(
    name='modelhub',
    version=VERSION,
    description='Modelhub',
    url="http://git.patsnap.com/research/modelhub",
    long_description=README,
    author='Jay Young(yjmade)',
    author_email='yangjian@patsnap.com',
    packages=find_packages(),
    install_requires=requirments,
    extras_require={
        "tf": ["tensorflow>=1.4.0"],
        "tfgpu": ["tensorflow-gpu>=1.4.0"],
        "tf_client": ["redis", "tensorflow>=1.4.0"],
        "tf_serving": ["redis"]
    },
    entry_points={
        'console_scripts': [
            'modelhub=modelhub.commands:main'
        ]
    },
)
