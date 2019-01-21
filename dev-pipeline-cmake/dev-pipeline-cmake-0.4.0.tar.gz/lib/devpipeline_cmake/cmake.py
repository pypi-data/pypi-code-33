#!/usr/bin/python3

"""This modules supports building CMake projects."""

import os.path
import re

import devpipeline_core.toolsupport
import devpipeline_build


class CMake:

    """This class manages the details of building using CMake."""

    def __init__(self, ex_args, target_config, config_args):
        self._ex_args = ex_args
        self._config_args = config_args
        self._target_config = target_config
        self._build_type = None

    def set_build_type(self, build_type):
        self._build_type = build_type

    def _get_build_flags(self):
        if self._build_type:
            return ["--config", self._build_type]
        return []

    def get_key_args(self):
        return self._config_args

    def configure(self, src_dir, build_dir, **kwargs):
        """This function builds the cmake configure command."""
        del kwargs
        ex_path = self._ex_args.get("project_path")
        if ex_path:
            src_dir = os.path.join(src_dir, ex_path)

        return [{"args": ["cmake", src_dir] + self._config_args, "cwd": build_dir}]

    def build(self, build_dir, **kwargs):
        """This function builds the cmake build command."""
        # pylint: disable=no-self-use
        del kwargs
        args = ["cmake", "--build", build_dir]
        args.extend(self._get_build_flags())
        return [{"args": args}]

    def install(self, build_dir, install_dir=None, **kwargs):
        """This function builds the cmake install command."""
        # pylint: disable=no-self-use
        del kwargs
        install_args = ["cmake", "--build", build_dir, "--target", "install"]
        install_args.extend(self._get_build_flags())
        if install_dir:
            self._target_config.env["DESTDIR"] = install_dir
        return [{"args": install_args}]


_ALL_CMAKE_ARGS = None


def _handle_cmake_arg(value, valid_fn):
    if value:
        return valid_fn(value)
    return []


_USABLE_ARG_FNS = {
    "args": lambda v: _handle_cmake_arg(v, lambda v: v),
    "prefix": lambda v: _handle_cmake_arg(
        v, lambda v: ["-DCMAKE_INSTALL_PREFIX={}".format(v)]
    ),
    "cc": lambda v: _handle_cmake_arg(v, lambda v: ["-DCMAKE_C_COMPILER={}".format(v)]),
    "cxx": lambda v: _handle_cmake_arg(
        v, lambda v: ["-DCMAKE_CXX_COMPILER={}".format(v)]
    ),
    "toolchain_file": lambda v: _handle_cmake_arg(
        v, lambda v: ["-DCMAKE_TOOLCHAIN_FILE={}".format(v)]
    ),
    "build_type": lambda v: _handle_cmake_arg(
        v, lambda v: ["-DCMAKE_BUILD_TYPE={}".format(v)]
    ),
    "generator": lambda v: _handle_cmake_arg(v, lambda v: ["-G", v]),
}

_USABLE_ARGS = {
    "args": devpipeline_core.toolsupport.ListSeparator(),
    "prefix": None,
    "cc": None,
    "cxx": None,
    "toolchain_file": None,
    "build_type": None,
    "generator": None,
}

_VALID_FLAG_SUFFIXES = ["debug", "minsizerel", "release", "relwithdebinfo"]


def _extend_flags_common(base_flags, suffix, value):
    if value:
        if suffix:
            base_flags += "_{}".format(suffix)
        return ["{}={}".format(base_flags, value)]
    else:
        return []


def _extend_cflags(base, suffix, value):
    return _extend_flags_common("-DCMAKE_{}_FLAGS".format(base), suffix, value)


def _make_common_args(arg_keys_list, prefix_string, suffix_string):
    new_args = devpipeline_core.toolsupport.build_flex_args_keys(
        [arg_keys_list, _VALID_FLAG_SUFFIXES]
    )
    prefix_pattern = re.compile(prefix_string)
    suffix_pattern = re.compile(suffix_string)
    ret_args = {}
    ret_fns = {}
    for arg in new_args:
        prefix_match = prefix_pattern.search(arg)
        suffix_match = suffix_pattern.search(arg)
        ret_args[arg] = " "
        ret_fns[arg] = lambda v, pm=prefix_match, sm=suffix_match: _extend_cflags(
            pm.group(1).upper(), sm.group(1).upper(), v
        )
    for arg in arg_keys_list:
        prefix_match = prefix_pattern.search(arg)
        ret_args[arg] = " "
        ret_fns[arg] = lambda v, pm=prefix_match: _extend_cflags(
            pm.group(1).upper(), None, v
        )
    return (ret_args, ret_fns)


_CFLAG_ARGS = ["cflags", "cxxflags"]


def _make_cflag_args():
    return _make_common_args(_CFLAG_ARGS, r"(.*)flags", r"\.(\w+)$")


def _extend_ldflags(base, suffix, value):
    return _extend_flags_common("-DCMAKE_{}_LINKER_FLAGS".format(base), suffix, value)


_LDFLAG_ARGS = ["exe", "module", "shared", "static"]


def _make_ldflag_args():
    base_args = devpipeline_core.toolsupport.build_flex_args_keys(
        [["ldflags"], _LDFLAG_ARGS]
    )
    return _make_common_args(base_args, r"ldflags\.(\w+)", r"\.(\w+)$")


_ARG_BUILDER_FUNCTIONS = [_make_cflag_args, _make_ldflag_args]


def _make_all_options():
    # pylint: disable=global-statement
    global _ALL_CMAKE_ARGS

    if not _ALL_CMAKE_ARGS:
        cmake_args = _USABLE_ARGS.copy()
        cmake_arg_fns = _USABLE_ARG_FNS.copy()
        for arg_builder in _ARG_BUILDER_FUNCTIONS:
            new_cmake_args, new_cmake_arg_fns = arg_builder()
            cmake_args.update(new_cmake_args)
            cmake_arg_fns.update(new_cmake_arg_fns)
        _ALL_CMAKE_ARGS = (cmake_args, cmake_arg_fns)
    return _ALL_CMAKE_ARGS


_EX_ARGS = {"project_path": None}

_EX_ARG_FNS = {"project_path": lambda v: ("project_path", v)}


def _make_cmake(config_info):
    """This function initializes a CMake builder for building the project."""
    configure_args = ["-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"]
    cmake_args = {}

    options, option_fns = _make_all_options()

    def _add_value(value, key):
        args_key, args_value = _EX_ARG_FNS[key](value)
        cmake_args[args_key] = args_value

    devpipeline_core.toolsupport.args_builder(
        "cmake",
        config_info,
        options,
        lambda v, key: configure_args.extend(option_fns[key](v)),
    )
    devpipeline_core.toolsupport.args_builder(
        "cmake", config_info, _EX_ARGS, _add_value
    )
    cmake = CMake(cmake_args, config_info, configure_args)
    build_type = config_info.config.get("cmake.build_type")
    if build_type:
        cmake.set_build_type(build_type)
    return devpipeline_build.make_simple_builder(cmake, config_info)
