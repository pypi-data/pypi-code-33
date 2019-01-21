"""
Basic file hash utilities
"""
import hashlib
import os
from json import loads
import re

BLOCKSIZE = 65536


def hash_file(filename, algorithm='sha1'):
    """
    Basic hash for a file
    :param filename: file path
    :param algorithm: see hashlib.algorithms_available
    :return: hex hash
    """
    hasher = getattr(hashlib, algorithm)()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
        afile.close()
    return hasher.hexdigest()


def hash_dir(directory, **kwargs):
    """
    Builds hashes for files in filesystem
    :param directory: directory to browse
    :param kwargs: additional arguments
    :return: array of dict of file information

    :Keyword Arguments:
        * *excludes* (``list``) --
          list of excluded paths
        * *verbose* (``bool``) --
          toggles verbose output
    """
    if not os.path.exists(directory):
        return None

    excludes = []
    if 'excludes' in kwargs:
        excludes = kwargs.get('excludes')

    r_files = {}
    path_len = len(directory)
    if not directory.endswith(os.sep):
        path_len += 1

    for root, dirs, files in os.walk(directory):
        dirs = [d for d in dirs if d not in excludes]
        files = [d for d in files if os.path.join(root[path_len:], d) not in excludes]

        for names in files:
            file_path = os.path.join(root, names)
            algorithm = 'sha1'
            if 'algorithm' in kwargs:
                algorithm = kwargs.get('algorithm')
            f_hash = hash_file(file_path, algorithm)
            r_files[file_path[path_len:]] = {
                'root': root[path_len:],
                'file': names,
                'hash': f_hash,
                'size': os.stat(file_path).st_size}
            if 'verbose' in kwargs:
                print('{} {}'.format(f_hash, names))
    return r_files


def check(directory, original, **kwargs):
    """
    Verifies if any changes appended in filesystem
    :param directory: directory to check
    :param original: json data file expected hashes
    :param kwargs: additional arguments
    :return: new array of dict of file information

    :Keyword Arguments:
        * *excludes* (``list``) --
          list of excluded paths
        * *verbose* (``bool``) --
          toggles verbose output
        * *dontcheck* (``list``) --
          list of patterns allowing to exclude files form check
          for example '/latest/'
    """
    c_hash = hash_dir(directory, **kwargs)
    o_hash = loads(original)
    dontcheck = ['dontcheck']
    if 'dontcheck' in kwargs:
        dontcheck = kwargs.get('dontcheck')
    for k in [k for k in o_hash.keys() for pattern in dontcheck if not re.search(pattern, k)]:
        if o_hash[k]['hash'] != c_hash[k]['hash']:
            raise ValueError("{} {} doesn't verify expected hash {}".format(
                c_hash[k]['hash'], k, o_hash[k]['hash']))
    return c_hash
