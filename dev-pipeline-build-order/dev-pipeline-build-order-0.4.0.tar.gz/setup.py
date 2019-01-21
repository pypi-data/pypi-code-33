#!/usr/bin/python3

from setuptools import setup, find_packages

with open("README.rst") as f:
    long_description = f.read()

_VERSION = "0.4.0"

setup(
    name="dev-pipeline-build-order",
    version=_VERSION,
    package_dir={"": "lib"},
    packages=find_packages("lib"),
    install_requires=[
        "dev-pipeline-configure >= {}".format(_VERSION),
        "dev-pipeline-core >= {}".format(_VERSION),
    ],
    entry_points={
        "devpipeline.drivers": [
            "build-order = devpipeline_buildorder.build_order:_BUILD_ORDER_COMMAND"
        ],
        "devpipeline.build_order.methods": [
            "dot = devpipeline_buildorder.dot:_DOT_TOOL",
            "graph = devpipeline_buildorder.dot:_GRAPH_TOOL",
            "layers = devpipeline_buildorder.dot:_LAYERS_TOOL",
            "list = devpipeline_buildorder:_LIST_TOOL",
        ],
    },
    author="Stephen Newell",
    description="build-order command for dev-pipeline",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-build-order",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
)
