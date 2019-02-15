# -*- coding:utf-8 -*-

import six
import os
import shutil
from ..path import *
from .mkdir import MKDIR
from .rm import RM

__all__ = ['copytree', 'CP']


def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    MKDIR(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if shutil.WindowsError is not None and isinstance(why, shutil.WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.append((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)


def CP(src, dest):
    raw_src = src
    raw_dest = dest

    if is_link(src):
        src = find_link_orig(src)

    src_has_slash = raw_src.endswith('/')
    dest_has_slash = raw_dest.endswith('/')
    if os.path.exists(dest):
        if is_link(dest):
            dest = find_link_orig(dest)

        if is_file(dest):
            if dest_has_slash:
                raise RuntimeError(u"CP dest {} is file, but ends with /".format(raw_dest))
            else:
                dest_type = 'file'
        else:
            dest_type = 'dir'
    else:
        dest_type = 'dir' if dest_has_slash else None

    if is_file(src):
        if dest_type == 'dir':
            true_dest = os.path.join(dest, BASENAME(raw_src))
        else:
            true_dest = dest

        MKDIR(DIRNAME(true_dest))
        RM(true_dest)
        shutil.copy(src, true_dest)
    else:
        if dest_type == 'file':
            raise RuntimeError(u"CP src {} is dir, but dest {} is file.".format(raw_src, raw_dest))

        if src_has_slash or (not src_has_slash and not dest_has_slash):
            true_dest = dest
        else:
            true_dest = os.path.join(dest, BASENAME(raw_src))

        MKDIR(true_dest)
        copytree(src, true_dest, symlinks=True)


