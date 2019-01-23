'''
fs defines a consistant api for working with the file system. 
It is made of wrapper functions for methods in os, shutil, tarfile, and pathlib.
'''

import os
import shutil
import tarfile
from pathlib import Path

# INTERFACE
def mv(src, dest):
    return os.replace(src, dest)

def rm(path):
    return os.remove(path)

def rimraf(path):
    return shutil.rmtree(path)

def basename(path):
    return os.path.basename(path)

def dirname(path):
    return os.path.dirname(path)

def mkdir(path):
    return os.mkdir(path) 

def mkfile(path):
    return Path(path).touch()

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

def listdir(path):
    return os.listdir(path) 

def exists(path):
    return Path(path).exists()

def is_dir(path):
    return Path(path).is_dir()

def copy(src, dest):
    return shutil.copyfile(src, dest)

def copy_dir(src, dest):
    return shutil.copytree(src, dest)

def link(src, dest):
    return os.link(src, dest)

def force_link(src, dest):
    if(exists(dest)):
        if(is_dir(dest)):
            rimraf(dest)
        else:
            rm(dest)
    return link(src, dest)


def chmod(path, permissions):
    return os.chmod(path, permissions)

        
def unpack_tarball(path):
    tar = tarfile.open(path, 'r:gz')
    tar.extractall()
    tar.close()
