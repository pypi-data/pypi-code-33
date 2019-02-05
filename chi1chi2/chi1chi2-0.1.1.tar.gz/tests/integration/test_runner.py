import os
import unittest
from collections import deque
from distutils.dir_util import copy_tree, remove_tree
from filecmp import dircmp
from importlib import import_module
from optparse import OptionParser
from pathlib import Path
from tempfile import mkdtemp
from time import sleep


def path_for_test(path):
    return os.path.join(os.path.dirname(__file__), path)


class ITTests(unittest.TestCase):
    def _run_it(self, param_dict):
        work_dir = mkdtemp()
        source = path_for_test(str(Path("input") / param_dict.get("case")))
        reference = path_for_test(str(Path("expected") / param_dict.get("case")))
        try:
            copy_tree(source, work_dir)
            os.chdir(work_dir)
            options = param_dict.get("options")
            module, method = _get_module_method(*param_dict.get("module-method"))
            module.options = options
            print(f"running method... {param_dict.get('module-method')}")
            method()
            print(f"running comparison for method... {param_dict.get('module-method')}")
            self._compare_dirs(reference, work_dir)
        finally:
            remove_tree(work_dir)

    def _compare_dirs(self, reference, work_dir):
        dcmp = dircmp(work_dir, reference)
        list_dirs = deque()
        self.assertListEqual(dcmp.left_list, dcmp.right_list, "files list differ")
        self.assertListEqual(dcmp.diff_files, [], f"differing files: {dcmp.diff_files}")
        list_dirs.extend(map(lambda dir: [str(Path(work_dir) / dir), str(Path(reference) / dir)], dcmp.subdirs))
        while not len(list_dirs) == 0:
            cur_work_dir, cur_reference = list_dirs.popleft()
            dcmp = dircmp(cur_work_dir, cur_reference)
            list_dirs.extend(
                map(lambda dir: [str(Path(cur_work_dir) / dir), str(Path(cur_reference) / dir)], dcmp.subdirs))
            self.assertListEqual(dcmp.left_list, dcmp.right_list, f"files list differ in subdirectory {cur_reference}")
            self.assertListEqual(dcmp.diff_files, [], f"differing files: {dcmp.diff_files}")


def _get_main_options(inp_file, lorentz_file, polar_prefix, lft_file, dist_prefix=None):
    return [
        ["-i", "input_file", inp_file],
        ["-l", "lorentz_file", lorentz_file],
        ["-p", "polar_prefix", polar_prefix],
        ["-L", "output_file_lft", lft_file],
        ["-d", "distributed_prefix", dist_prefix],
        ["-Q", "output_file_qlft", None],
    ]


def _get_input_preparator_options(inp_file, radius):
    return [
        ["-i", "input_file", inp_file],
        ["-r", "radius_cutoff", radius],
    ]


def _get_from_crystal_options(inp_file, opt_file, scf_file):
    return [
        ["-i", "input_file", inp_file],
        ["-t", "opt_file", opt_file],
        ["-s", "scf_file", scf_file],
        ["-o", "output_file", None],
        ["-X", "skip_produce_xyz", False],
    ]


def _get_from_fra_options(inp):
    return [
        ["-i", "input_file", inp],
        ["-o", "output_file", None],
        ["-f", "output_fra", None],
        ["-x", "output_xyz_file", None],
        ["-H", "skip_adj_hydr", False],
        ["-R", "skip_reorder", False],
        ["-X", "produce_xyz", False],
    ]


def _get_from_cif_options(inp):
    return [
        ["-i", "input_file", inp],
        ["-o", "output_file", None],
        ["-f", "output_fra", None],
        ["-x", "output_xyz_file", None],
        ["-H", "skip_adj_hydr", False],
        ["-R", "skip_reorder", False],
        ["-X", "produce_xyz", False],
    ]


def _get_module_method(module_name, method_name):
    module = import_module(module_name)
    method = getattr(module, method_name)
    return module, method


def _get_options(option_list):
    parser = OptionParser()
    for opt_list in option_list:
        parser.add_option(opt_list[0], dest=opt_list[1], default=opt_list[2])
    options, _ = parser.parse_args()
    return options
