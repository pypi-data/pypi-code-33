"""Remap"""
import argparse
import importlib.util
import json
import os
from collections import Iterable, OrderedDict

from tatau.fs.dirs import list_files


def make_tree(files_list: Iterable, path_sep: str = "/") -> OrderedDict:
    """
    Collect files tree

    :param files_list: list of files
    :param path_sep: path separator
    :return: files tree
    """
    root_dir = OrderedDict()
    for path in sorted(files_list):
        path_strip = path.strip("/")
        items = path_strip.split(path_sep)

        current_dir = root_dir
        if len(items) > 1:
            for item_idx, item in enumerate(items[:-1]):
                if item not in current_dir:
                    if item_idx == len(items) - 2:
                        current_dir[item] = []
                    else:
                        current_dir[item] = OrderedDict()

                current_dir = current_dir[item]

                if item_idx == len(items) - 2:
                    current_dir.append(path)
    return root_dir


def remap_tree(files_list: Iterable, remap_script_path: str, path_sep="/"):
    """
    Load user custom remap script and invoke remap

    :param files_list: List of files to remap
    :param remap_script_path: path to the user define remap script
    :param path_sep: Path separator
    :return: Ordered chunks tree
    """
    name = os.path.basename(remap_script_path)
    name = name.split(".")[0]
    spec = importlib.util.spec_from_file_location(name=name, location=remap_script_path)
    module = importlib.util.module_from_spec(spec)

    if module is None:
        raise RuntimeError("Remap script load error")

    spec.loader.exec_module(module)

    if not hasattr(module, 'remap') or not callable(module.remap):
        raise RuntimeError("remap function doesn't exists")

    files_tree = make_tree(files_list=files_list, path_sep=path_sep)

    return module.remap(files_tree=files_tree)


def main():
    """Test Remap"""
    parser = argparse.ArgumentParser(description='Remap Dataset')
    parser.add_argument('-d', '--dir', type=str, required=True, help='Dataset path')
    parser.add_argument('-s', '--script', type=str, required=True, help='Remap script path')
    args = parser.parse_args()
    tree = remap_tree(files_list=list_files(args.dir), remap_script_path=args.script)
    print(json.dumps(tree, indent=3))


if __name__ == "__main__":
    main()
