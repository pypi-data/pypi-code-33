#!/usr/bin/python3

from setuptools import setup, find_packages

with open("README.rst") as f:
    long_description = f.read()

_VERSION = "0.4.0"

setup(
    name="dev-pipeline-build",
    version=_VERSION,
    package_dir={"": "lib"},
    packages=find_packages("lib"),
    install_requires=[
        "dev-pipeline-core >= {}".format(_VERSION),
        "dev-pipeline-configure >= {}".format(_VERSION),
    ],
    entry_points={
        "devpipeline.drivers": ["build = devpipeline_build.build:_BUILD_COMMAND"],
        "devpipeline.builders": [
            "nothing = devpipeline_build.builder:_NOTHING_BUILDER"
        ],
        "devpipeline.config_modifiers": [
            "initialize_artifact_paths = devpipeline_build:_initialize_artifact_paths",
            "build_dir = devpipeline_build:_make_build_dir",
        ],
        "devpipeline.config_sanitizers": [
            "missing-build-option = devpipeline_build.builder:_no_build_check",
            "deprecated-no-install = devpipeline_build.builder:_deprecated_no_install_check",
            "deprecated-install-path = devpipeline_build.builder:_deprecated_install_path_check",
            "no-install-artifact-paths = devpipeline_build.builder:_no_install_artifact_paths",
        ],
    },
    author="Stephen Newell",
    description="build tooling for dev-pipeline",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-build",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
    ],
)
