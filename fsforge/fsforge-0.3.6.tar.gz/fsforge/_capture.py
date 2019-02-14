# -*- coding: utf-8 -*-

import fnmatch
import os
import re


FileNotRead = None


class FsForgeError(TypeError):
    pass


class PathElement(object):
    __slots__ = ("_value", "_matcher")

    def __init__(self, value):
        try:
            self._value = str(value)
        except Exception:
            own_type = self.__class__.__name__
            other_type = type(value).__name__
            raise TypeError("Cannot create {} out of {}".format(own_type, other_type))

        self._matcher = re.compile(fnmatch.translate(self._value))

    def __str__(self):
        return self._value

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self._value)

    def __eq__(self, other):
        return str(self) == str(other)

    def __contains__(self, other):
        """
            comparing them we will check if one contains another
            e.g. 'file.txt' in 'that_file.txt' should give negative result,
            but 'file.txt' in '*file.txt' is supposed to be True

        """
        if isinstance(other, (PathElement, str)):
            return self._matcher.match(str(other))


def iddle_file_processor(_):
    return FileNotRead


def reading_file_processor(file_path):
    with open(file_path, "r") as ff:
        return ff.read()


def _masks(tree_masks):
    for mask in tree_masks:
        if isinstance(mask, dict):
            for name_pattern, masks_def in mask.items():
                yield name_pattern, masks_def


def _matching_dir_masks(tree_masks, dir_name):
    def collect():
        for name_pattern, sub_masks_def in _masks(tree_masks):
            if dir_name in PathElement(name_pattern):
                if name_pattern == "**":
                    yield {name_pattern: sub_masks_def}
                else:
                    yield sub_masks_def
    return list(collect())


def _matching_file_processor(tree_masks, file_name):
    def collect():
        for name_pattern, processor in _masks(tree_masks):
            if name_pattern == "**" and isinstance(processor, dict):
                for sub_name_pattern, sub_proccessor in processor.items():
                    if file_name in PathElement(sub_name_pattern):
                        yield sub_name_pattern, sub_proccessor
            else:
                if file_name in PathElement(name_pattern) and not isinstance(processor, dict):
                    yield name_pattern, processor

    matching_rules = list(collect())
    if matching_rules:
        patterns, processors = list(zip(*collect()))
        if len(processors) > 1:
            # try to filter-out processors specified for wildcard paths

            processors = [proc for pattern, proc in matching_rules if pattern not in ("*", "**")]
            if len(processors) == 1:
                return processors[0]

            msg = "Unable to distinguish a file processor for a file named: {}. Each of following patterns matches: {}"
            raise FsForgeError(msg.format(file_name, ", ".join(repr(p) for p in patterns)))
        return processors[0]


def take_fs_snapshot(start_fs_path, path_masks={"**": iddle_file_processor}):
    """
        It's supposed to be a helper to scan a FS. E.g. to recreate the scanned file system as a fake fs for tests.

        Returns nested structure of dictionaries. Keys are names (of directories and files), values are either:
         - nested dicts for directories,
         - None or given file content in case of files.

        Having such a tree in a filesystem:
        /tmp/ex
        ├── dir_a
        │   ├── sub_empty_dir
        │   ├── sub_dir_with_a_file
        │   │   └── file_1.txt
        │   └── file_2.txt
        ├── dir_b
        │   ├── special_file.txt
        │   └── file_4.bin
        └── empty_dir

        # python:
        >>> take_fs_snapshot('/tmp/ex')
        {
            'dir_a': {
                'sub_empty_dir': {},
                'sub_dir_with_a_file': {'file_1.txt': FileNotRead},
                'file_2.txt': FileNotRead,
            },
            'dir_b': {'special_file.txt': FileNotRead, 'file_4.bin': FileNotRead},
            'empty_dir': {}
        }
    """

    def build_a_tree(current_fs_path, masks):
        for root, directories, files in os.walk(current_fs_path):

            for dir_name in directories:
                current_masks = _matching_dir_masks(masks, dir_name)
                if current_masks:
                    sub_dir_path = os.path.join(root, dir_name)
                    yield dir_name, dict(build_a_tree(sub_dir_path, current_masks))

            for file_name in files:
                file_processor = _matching_file_processor(masks, file_name)
                if file_processor:
                    sub_file_path = os.path.join(root, file_name)
                    yield file_name, file_processor(sub_file_path)

            # Quit immediately after first directory level.
            # We go deeper by recursiveness not with os.walk.
            break

    return dict(build_a_tree(start_fs_path, [path_masks]))
