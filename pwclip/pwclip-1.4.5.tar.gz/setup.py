#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Generic Setup script, takes package info from __pkginfo__.py file.
"""
from sys import argv
from os import listdir, chdir, getcwd, path
from setuptools import setup, find_packages

__docformat__ = "restructuredtext en"

def tabl(dats, ind=0, iind=0):
    """list to string with indentations"""
    tabbl = ''
    for i in dats:
        if isinstance(i, (tuple, list)):
            iind = int(max(len(i) for i in dats)+ind)
            tabbl = '%s\n%s'%(tabbl, tabl(i, iind))
            continue
        tabbl = '%s\n%s%s'%(tabbl, ' '*ind, i)
    return tabbl.lstrip('\n')

def tabd(dats, ind=0, iind=0):
    """
    this is a function where i try to guess the best indentation for text
    representation of keyvalue paires with best matching indentation
    e.g:
    foo         = bar
    a           = b
    blibablubb  = bla
    ^^indent "bar" and "b" as much as needed ("add" is added to each length)
    """
    try:
        lim = int(max(len(str(k)) for k in dats if k)+int(ind))
    except ValueError:
        return dats
    tabbd = ''
    try:
        print(dats)
        for (key, val) in dats.items():
            spc = ' '*int(lim-len(str(key)))
            if val and isinstance(val, dict):
                tabbd = '%s\n%s%s:\n%s'%(tabbd, ' '*ind, key, tabd(
                    val, ind+int(iind if iind else 2), iind if iind else 2))
            else:
                tabbd = str('%s\n%s%s%s = %s'%(
                    tabbd, ' '*ind, key, spc, val)).strip('\n')
    except AttributeError:
        return tabl(dats, ind)
    return tabbd.strip('\n')

def packages(directory):
    """return a list of subpackages for the given directory"""
    result = []
    for package in listdir(directory):
        absfile = path.join(directory, package, '__init__.py')
        if path.exists(absfile):
            result.append(path.dirname(absfile))
            result += packages(path.dirname(absfile))
    return result

def scripts(linux_scripts):
    """creates the proper script names required for each platform"""
    from distutils import util
    if util.get_platform()[:3] == 'win':
        return linux_scripts + [script + '.bat' for script in linux_scripts]
    return linux_scripts

if __name__ == '__main__':
    kwargs = {}
    kwargs['packages'] = ['pwclip'] + packages('pwclip')
    with open(path.join('pwclip', '__pkginfo__.py'), 'r') as f:
        __pkginfo = f.read()
        exec(__pkginfo, kwargs)
    if '--pybuilder' in argv:
        print(tabd(dict(sorted(kwargs.items()))))
        input('\npress Enter to continue...')
        del argv[argv.index('--pybuilder')]
    try:
        setup(**kwargs)
    except (KeyboardInterrupt, TypeError):
        exit(1)
    exit(0)
