#!/usr/bin/python3

"""
Root module for the build-order tool.
"""

import devpipeline_core.resolve


# For some reason, setup.py can't find this in the build_order moudle.  Move it
# back when I figure out why.
def _print_list(targets, components):
    build_order = devpipeline_core.resolve.order_dependencies(targets, components)
    print(build_order)


_LIST_TOOL = (_print_list, "Print a sequential order of components.")
