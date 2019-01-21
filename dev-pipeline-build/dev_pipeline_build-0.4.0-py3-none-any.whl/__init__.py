#!/usr/bin/python3

"""
Root module for the build plugin.  It provides the BUILDERS dictionary, which
contains every builder plugin.
"""

import os.path

import devpipeline_core.plugin

BUILDERS = devpipeline_core.plugin.query_plugins("devpipeline.builders")


def _make_build_dir(configuration):
    for name, config in configuration.items():
        if "import" in config:
            config.set("dp.build_dir", "")
        else:
            config.set("dp.build_dir", os.path.join(config.get("dp.build_root"), name))


def _initialize_artifact_paths(configuration):
    def _split_val(val):
        index = val.find("=")
        return (val[:index], val[index + 1 :])

    for name, config in configuration.items():
        del name
        for val in config.get_list("build.artifact_paths"):
            key, required = _split_val(val)
            del required
            config.set("dp.build.artifact_path.{}".format(key), "NOTFOUND")


class _SimpleBuild(devpipeline_core.toolsupport.SimpleTool):

    """This class does a simple build - configure, build, and install."""

    def __init__(self, real, current_target):
        super().__init__(current_target, real)

    def get_key_args(self):
        # pylint: disable=missing-docstring
        return self.real.get_key_args()

    def configure(self, *args, **kwargs):
        # pylint: disable=missing-docstring
        self._call_helper("Configuring", self.real.configure, *args, **kwargs)

    def build(self, *args, **kwargs):
        # pylint: disable=missing-docstring
        self._call_helper("Building", self.real.build, *args, **kwargs)

    def install(self, *args, **kwargs):
        # pylint: disable=missing-docstring
        self._call_helper("Installing", self.real.install, *args, **kwargs)


def make_simple_builder(real_builder, configuration):
    """
    Create an Build instance that leverages executors.

    Arguments:
    real_builder - a class instance that provides an Build interface
    configuration - the configuration for the Build target
    """
    return _SimpleBuild(real_builder, configuration)
