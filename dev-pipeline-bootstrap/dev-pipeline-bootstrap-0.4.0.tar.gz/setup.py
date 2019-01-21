#!/usr/bin/python3

from setuptools import setup, find_packages

with open("README.rst") as f:
    long_description = f.read()

_VERSION = "0.4.0"

setup(
    name="dev-pipeline-bootstrap",
    version=_VERSION,
    package_dir={"": "lib"},
    packages=find_packages("lib"),
    install_requires=[
        "dev-pipeline-configure >= {}".format(_VERSION),
        "dev-pipeline-core >= {}".format(_VERSION),
        "dev-pipeline-build >= {}".format(_VERSION),
        "dev-pipeline-scm >= {}".format(_VERSION),
    ],
    entry_points={
        "devpipeline.drivers": [
            "bootstrap = devpipeline_bootstrap.bootstrap:_BOOTSTRAP_COMMAND"
        ]
    },
    author="Stephen Newell",
    description="build tooling for dev-pipeline",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-bootstrap",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities",
    ],
)
