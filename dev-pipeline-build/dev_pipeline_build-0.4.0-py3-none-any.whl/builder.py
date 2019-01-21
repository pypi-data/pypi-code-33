#!/usr/bin/python3
"""This modules aggregates the available builders that can be used."""

import hashlib
import os.path
import os
import re

import devpipeline_core.paths
import devpipeline_core.toolsupport

import devpipeline_build


def _nothing_builder(current_config):
    # Unused variables
    del current_config

    class _NothingBuilder:
        def configure(self, src_dir, build_dir):
            # pylint: disable=missing-docstring
            pass

        def build(self, build_dir):
            # pylint: disable=missing-docstring
            pass

        def install(self, build_dir, install_dir):
            # pylint: disable=missing-docstring
            pass

        def get_key_args(self):
            # pylint: disable=missing-docstring,no-self-use
            return []

    return _NothingBuilder()


_NOTHING_BUILDER = (_nothing_builder, "Do nothing.")
_BUILD_TOOL_KEYS = ["build.tool", "build"]
_NO_INSTALL_KEYS = ["build.no_install", "no_install"]
_INSTALL_PATH_KEYS = ["build.install_path", "install_path"]


def _find_key(component, keys):
    for key in keys:
        if key in component:
            return key
    return None


def _final_deprecated_check(real_key, expected_key, component_name, error_fn):
    if real_key and (real_key != expected_key):
        error_fn(
            "{}: {} is deprecated; migrate to {}".format(
                component_name, real_key, expected_key
            )
        )


def _check_deprecated_helper(configuration, keys, error_fn):
    for name, config in configuration.items():
        key = _find_key(config, keys)
        _final_deprecated_check(key, keys[0], name, error_fn)


def _no_build_check(configuration, error_fn):
    for name, config in configuration.items():
        build_key = _find_key(config, _BUILD_TOOL_KEYS)
        if not build_key:
            error_fn("No builder declared in {}".format(name))
        _final_deprecated_check(build_key, _BUILD_TOOL_KEYS[0], name, error_fn)


def _deprecated_no_install_check(configuration, error_fn):
    _check_deprecated_helper(configuration, _NO_INSTALL_KEYS, error_fn)


def _deprecated_install_path_check(configuration, error_fn):
    _check_deprecated_helper(configuration, _INSTALL_PATH_KEYS, error_fn)


def _no_install_artifact_paths(configuration, error_fn):
    for name, config in configuration.items():
        if "build.artifact_paths" in config:
            key = _find_key(config, _NO_INSTALL_KEYS)
            if key:
                error_fn(
                    "{} - Cannot use build.artifact_paths with {}".format(name, key)
                )


def _make_builder(config, current_target):
    """
    Create and return a Builder for a component.

    Arguments
    component - The component the builder should be created for.
    """
    tool_key = devpipeline_core.toolsupport.choose_tool_key(
        current_target, _BUILD_TOOL_KEYS
    )

    return devpipeline_core.toolsupport.tool_builder(
        config, tool_key, devpipeline_build.BUILDERS, current_target
    )


def _find_folder(file, path):
    for root, dirs, files in os.walk(path):
        del dirs
        if file in files:
            # return os.path.join(root, file)
            return root
    return ""


def _find_file_paths(component, install_path):
    def _split_val(val):
        index = val.find("=")
        return (val[:index], val[index + 1 :])

    for val in component.get_list("build.artifact_paths"):
        key, required = _split_val(val)
        found_path = _find_folder(required, install_path)
        component.set("dp.build.artifact_path.{}".format(key), found_path)


_IGNORE_KEY_PATTERN = re.compile(r"^dp\.")
_WHITELISTED_KEYS = ["dp.profile_name", "dp.overrides"]


def _guess_build_dir(target_configuration, hasher):
    for key in sorted(target_configuration):
        match = _IGNORE_KEY_PATTERN.match(key)
        if not match or (match and (key in _WHITELISTED_KEYS)):
            hash_key = "{}={}".format(key, target_configuration.get(key))
            hasher.update(hash_key.encode("utf-8"))


def _get_build_path(target_configuration, builder):
    build_dir = target_configuration.get("dp.build_dir")
    if not build_dir:
        # deal with imported packages
        hasher = hashlib.sha256()
        try:
            for val in builder.get_key_args():
                hasher.update(val.encode("utf-8"))
        except AttributeError:
            _guess_build_dir(target_configuration, hasher)
        hasher.update(target_configuration.get("dp.src_dir").encode("utf-8"))
        build_dir = devpipeline_core.paths.make_path(
            target_configuration,
            "build.cache",
            target_configuration.get("dp.import_name"),
            target_configuration.get("dp.import_version"),
            hasher.hexdigest(),
        )
        target_configuration.set("dp.build_dir", build_dir)
    return build_dir


def build_task(current_target):
    """
    Build a target.

    Arguments
    target - The target to build.
    """

    target = current_target.config
    try:
        builder = _make_builder(target, current_target)
        build_path = _get_build_path(target, builder)
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        builder.configure(src_dir=target.get("dp.src_dir"), build_dir=build_path)
        builder.build(build_dir=build_path)
        no_install = devpipeline_core.toolsupport.choose_tool_key(
            current_target, _NO_INSTALL_KEYS
        )
        if no_install not in target:
            install_path = target.get(
                devpipeline_core.toolsupport.choose_tool_key(
                    current_target, _INSTALL_PATH_KEYS
                ),
                fallback="install",
            )
            builder.install(build_dir=build_path, install_dir=install_path)
            _find_file_paths(target, os.path.join(build_path, install_path))
    except devpipeline_core.toolsupport.MissingToolKey as mtk:
        current_target.executor.warning(mtk)
