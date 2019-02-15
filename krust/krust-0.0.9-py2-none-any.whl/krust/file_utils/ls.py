# -*- coding:utf-8 -*-

import six
import os
import re

import glob
from .path import P, is_glob, is_hidden, is_file, is_dir, ensure_slash
from krux.regex import grep, simple_pattern_to_regex


__all__ = [
    'sorted_walk',
    'LS', 'LS_R', 'LS_GREP'
]


# status: done
def sorted_walk(top, **kwargs):
    """returns the sorted result in a list consisting os.walk's 3-tuple: (dirpath, dirnames, filename).
    kwargs: os.path's kwargs, i.e. topdown=True[, onerror=None[, followlinks=False]]"""
    kwargs.setdefault('followlinks', True)
    w = os.walk(top, **kwargs)
    res = list(w)
    res.sort()
    for stuff in res:
        stuff[1].sort()
        stuff[2].sort()
    return res


def LS(root=None, pattern=None, parse_info=False, recursive=False, with_root=None, ignore_hidden=True, use_glob=None, **kwargs):
    root = P(root)
    root_is_glob = use_glob is not False and is_glob(root)
    pattern_is_base_only = pattern is not None and '/' not in pattern  # TODO: support compiled regex pattern

    result = []
    roots = []
    if root_is_glob:
        glob_result = sorted(glob.glob(root))
        if not recursive:
            for full_fname in glob_result:
                if ignore_hidden:
                    sub_paths = full_fname.split('/')  # TODO: Windows compatibility.
                    if True in [is_hidden(sub) for sub in sub_paths]:
                        continue

                if root.endswith('/'):
                    roots.append(full_fname)
                else:
                    result.append(full_fname)
        else:
            for full_fname in glob_result:
                if is_file(full_fname):
                    result.append(full_fname)
                elif is_dir(full_fname):
                    roots.append(full_fname)
    else:
        roots.append(root)

    kwargs.setdefault('followlinks', True)
    for root in roots:
        if root is None:
            safe_root = '.'
        else:
            safe_root = root

        if recursive:
            walk_tuple_list = sorted_walk(safe_root, **kwargs)
        else:
            fnames = sorted(os.listdir(safe_root))
            walk_tuple_list = [(safe_root, [], fnames)]

        part_result = []
        for walk_tuple in walk_tuple_list:
            d = walk_tuple[0]

            if ignore_hidden:
                sub_dirs = d.split('/')  # TODO: Windows compatibility.
                if True in [is_hidden(sub_dir) for sub_dir in sub_dirs[1:]]:  # skip root
                    continue

            for fname in walk_tuple[2]:
                if ignore_hidden and is_hidden(fname):
                    continue
                full_fname = os.path.join(d, fname)
                part_result.append(full_fname)

        if not root_is_glob and not with_root:
            root_length = len(ensure_slash(safe_root))
            part_result = [full_fname[root_length:] for full_fname in part_result]

        result.extend(part_result)

    if pattern:
        fnames_to_match = [os.path.basename(full_fname) if pattern_is_base_only else full_fname for full_fname in result]
        if isinstance(pattern, six.string_types):
            pattern = simple_pattern_to_regex(pattern, sep_chars='/')
        return grep(pattern, fnames_to_match, parse_info=parse_info)
    else:
        return result


def LS_R(root=None, pattern=None, parse_info=False, with_root=None, ignore_hidden=True, use_glob=None, **kwargs):
    kwargs.pop('recursive', None)
    return LS(root=root, pattern=pattern, parse_info=parse_info, recursive=True, with_root=with_root, ignore_hidden=ignore_hidden, use_glob=use_glob, **kwargs)


def LS_GREP(root=None, pattern=None, recursive=True, with_root=None, ignore_hidden=True, use_glob=None, **kwargs):
    kwargs.pop('parse_info', None)
    return LS(root=root, pattern=pattern, parse_info=True, recursive=recursive, with_root=with_root, ignore_hidden=ignore_hidden, use_glob=use_glob, **kwargs)


# def LS_GROUP(top=None, pattern=r'(.*)', fast=True, keys=None, exclude_keys=None):
#     grep_res = LS_GREP(top=top, pattern=pattern, fast=fast)
#
#     group_paras = {}
#     groups = {}
#     for fname, info in grep_res:
#         if keys:
#             d = {}
#             for k in keys:
#                 if k in info:
#                     d[k] = info[k]
#         else:
#             d = info.copy()
#
#         to_pop = set(exclude_keys) if exclude_keys else set()
#         for k in d:
#             if isinstance(k, int):
#                 to_pop.add(k)
#
#         for k in to_pop:
#             d.pop(k, None)
#
#         keystr = dict2str(d)
#         group_paras.setdefault(keystr, d)
#         fnames = groups.setdefault(keystr, [])
#         fnames.append(fname)
#
#     res = []
#     for keystr in sorted(groups.keys()):
#         res.append((groups[keystr], group_paras[keystr]))
#
#     return res

