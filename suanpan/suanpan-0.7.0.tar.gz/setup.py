#!/usr/bin/env python

"""
suanpan
"""
import os

from setuptools import find_packages, setup

INSTALL_REQUIRES = [
    "imageio==2.4.1",
    "numpy==1.15.2",
    "opencv-python==3.4.3.18",
    "pandas==0.23.4",
    "tqdm==4.28.1",
    "retrying==1.3.3",
]
EXTRAS_REQUIRE = {
    "service": [
        "googleapis-common-protos==1.6.0b6",
        "grpcio-tools==1.16.1rc1",
        "oss2==2.5.0",
        "sasl==0.2.1",
        "thrift-sasl==0.3.0",
        "thrift==0.11.0",
        "pyhive[hive]==0.6.1",
    ],
    "docker": [
        "oss2==2.5.0",
        "sasl==0.2.1",
        "thrift-sasl==0.3.0",
        "thrift==0.11.0",
        "pyhive[hive]==0.6.1",
    ],
}
README = "README.md"


def read_file(path):
    with open(path, "r") as f:
        return f.read()


fix_packages = ["__suanpan__"]
packages = find_packages()
packages.extend(fix_packages)

setup(
    name="suanpan",
    version="0.7.0",
    packages=packages,
    license="See License",
    author="majik",
    author_email="me@yamajik.com",
    description=read_file(README),
    long_description=__doc__,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
