#!/usr/bin/python3
"""This module initiates the build."""

import argparse

import devpipeline_core.command
import devpipeline_configure.cache

import devpipeline_build.builder


def _list_builders():
    for builder in sorted(devpipeline_build.BUILDERS):
        print("{} - {}".format(builder, devpipeline_build.BUILDERS[builder][1]))


_MAJOR = 0
_MINOR = 4
_PATCH = 0

_STRING = "{}.{}.{}".format(_MAJOR, _MINOR, _PATCH)


class BuildCommand(devpipeline_core.command.TaskCommand):
    """Class to provide build functionality to dev-pipeline."""

    def __init__(self, config_fn):
        super().__init__(
            config_fn=config_fn,
            tasks=[devpipeline_build.builder.build_task],
            prog="dev-pipeline build",
            description="Build targets",
        )
        self.add_argument(
            "--list-builders",
            action="store_true",
            default=argparse.SUPPRESS,
            help="List the available builder tools",
        )
        self.helper_fn = lambda: super(BuildCommand, self).process()
        self.set_version(_STRING)

    def setup(self, arguments):
        if "list_builders" in arguments:
            self.helper_fn = _list_builders

    def process(self):
        self.helper_fn()


def main(args=None, config_fn=devpipeline_configure.cache.update_cache):
    # pylint: disable=missing-docstring
    builder = BuildCommand(config_fn)
    # pylint: disable=missing-docstring
    devpipeline_core.command.execute_command(builder, args)


_BUILD_COMMAND = (main, "Build and install a set of components.")

if __name__ == "__main__":
    main()
