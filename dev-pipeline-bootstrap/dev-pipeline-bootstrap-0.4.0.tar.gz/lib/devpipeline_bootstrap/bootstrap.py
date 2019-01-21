#!/usr/bin/python3

"""
This module does a checkout and build of the packages given in the config file.
"""

import devpipeline_core.command
import devpipeline_configure.cache

import devpipeline_build.builder
import devpipeline_scm.scm

_MAJOR = 0
_MINOR = 3
_PATCH = 0

_STRING = "{}.{}.{}".format(_MAJOR, _MINOR, _PATCH)


def main(args=None, config_fn=devpipeline_configure.cache.update_cache):
    # pylint: disable=bad-continuation,missing-docstring
    builder = devpipeline_core.command.make_command(
        [devpipeline_scm.scm.scm_task, devpipeline_build.builder.build_task],
        config_fn=config_fn,
        prog="dev-pipeline bootstrap",
        description="Checkout and build packages",
    )
    builder.set_version(_STRING)
    devpipeline_core.command.execute_command(builder, args)


_BOOTSTRAP_COMMAND = (
    main,
    "Checkout and build a project.  "
    "This is most useful right after a fresh configure.",
)

if __name__ == "__main__":
    main()
