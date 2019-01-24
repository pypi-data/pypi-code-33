import os

import xattr

def set(filename, key, value=''):
    xattr.set(filename, key, value)


def get(filename):
    attrs = xattr.get_all(filename)
    return [ (str(k, 'utf-8'), str(v, 'utf-8')) for k,v in attrs ]


def rm(filename, key):
    xattr.remove(filename, key)


def dir(foldername):
    dst_folder = 'marks'
    for root, dirs, files in os.walk(foldername, topdown=True):
        for name in files:
            make_link(root, name, dst_folder)


def make_link(root, filename, dst_folder):
    filepath = os.path.join(root, filename)
    original_filepath = os.path.join('..', '..', '..', filepath)
    for k, v in xattr.get_all(filepath):
        k = str(k, 'utf-8')
        v = str(v, 'utf-8')
        v_dir = os.path.join(dst_folder, k, v)
        os.makedirs(v_dir)

        new_filepath = os.path.join(v_dir, filename)
        os.symlink(original_filepath,  new_filepath)
