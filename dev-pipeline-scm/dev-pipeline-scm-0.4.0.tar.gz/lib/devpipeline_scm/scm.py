#!/usr/bin/python3
"""This module implements some helper functions and a simple SCM tool."""

import devpipeline_core.plugin
import devpipeline_core.toolsupport

import devpipeline_scm


def _nothing_scm(current_target):
    # Unused variables
    del current_target

    class _NothingScm:
        def checkout(self, repo_dir, shared_dir):
            # pylint: disable=missing-docstring
            pass

        def update(self, repo_dir):
            # pylint: disable=missing-docstring
            pass

    return _NothingScm()


_NOTHING_SCM = (_nothing_scm, "Do nothing.")


def _make_scm(current_target):
    """
    Create an Scm for a component.

    Arguments
    component - The component being operated on.
    """
    # pylint: disable=protected-access
    tool_key = devpipeline_core.toolsupport.choose_tool_key(
        current_target, devpipeline_scm._SCM_TOOL_KEYS
    )

    return devpipeline_core.toolsupport.tool_builder(
        current_target.config, tool_key, devpipeline_scm.SCMS, current_target
    )


def scm_task(current_target):
    """
    Update or a local checkout.

    Arguments
    target - The target to operate on.
    """
    try:
        scm = _make_scm(current_target)
        src_dir = current_target.config.get("dp.src_dir")
        shared_dir = current_target.config.get("dp.src_dir_shared")
        scm.checkout(repo_dir=src_dir, shared_dir=shared_dir)
        scm.update(repo_dir=src_dir)
    except devpipeline_core.toolsupport.MissingToolKey as mtk:
        current_target.executor.warning(mtk)
