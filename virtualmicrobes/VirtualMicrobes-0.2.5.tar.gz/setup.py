#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Created on Dec 2, 2013

This setup.py script follows as much as possible the advice of Jeff Knupp in his guide
'Open Sourcing a Python Project the Right Way'
(https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)

In addition, to build cython extension modules it follows the guide on automatic
detection and compiling of extension files:
https://github.com/cython/cython/wiki/PackageHierarchy.

uploaded with python setup.py sdist upload 

@author: thocu
'''
from __future__ import absolute_import
#from __future__ import print_function

import io
import os
import re
import sys
import inspect
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import relpath
from os.path import splitext

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand

try:
    # Allow installing package without any Cython available. This
    # assumes you are going to include the .c files in your sdist.
    import Cython
    import cython_gsl
    print "Cython = \t\t[OKAY]"
except ImportError:
    print "You don't seem to have Cython installed. You can get a"
    print "copy from www.cython.org and install it."
    print "Going to use generated c sources instead to build extensions."
    Cython = None
    import find_gsl as cython_gsl

try:
    import numpy
    print "numpy = \t\t[OKAY]"
except ImportError:
    print "You don't seem to have numpy installed. Please run 'sudo apt-get install numpy'"

try:
    from PyQt4.Qt import PYQT_VERSION_STR
    print "PyQt4 = \t\t[OKAY]"
except ImportError:
    print "You don't seem to have pyqt-4 installed. Please run 'pip install python-qt4'"

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

def do_setup(run_here=None, *args):
    if len(args):
        orig_sys_argv = sys.argv
        sys.argv = args
    curdir = os.path.abspath(os.curdir)
    if run_here is None:
        run_here = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
    print run_here
    os.chdir(run_here)
    # finally, we can pass all this to distutils
    print sys.argv
    data_files = []
    for (path, dir, fns) in os.walk('utility_files'):
        for fn in fns:
            data_files.append(os.path.join(path,fn))
    setup(
        name="VirtualMicrobes",
        version='0.2.5',
        author="Thomas D. Cuypers, Bram van Dijk",
        author_email="thomas.cuypers@gmail.com, bramvandijk88@gmail.com",
        url="https://bitbucket.org/thocu/virtualmicrobes",
        packages=find_packages('src'),
        package_dir={'': 'src'},
        data_files=[('utility_files',data_files)],
        py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
        include_package_data=True,

        #package_data={"src/VirtualMicrobes/cython_gsl_interface": ["*.pxd"]},
        test_suite='VirtualMicrobes.tests.test_VirtualMicrobes',
        description='Virtual Microbe Evolutionary Simulator',
        long_description='%s\n%s' % (
            re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
            re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
        ),
        setup_requires=[
            'cython','CythonGSL'
            ] if Cython else [],
        #setup_requires=['Cython>=0.24','CythonGSL'],
        install_requires=['attrdict==1.1.0',
                          'blessings>=1.6',
                          #'Cython>=0.24',
                          #'CythonGSL',
                          #'ete3',
                          #'pyqt',  ete3 requires pyqt, but it cannot be 'pip install'ed
                          'matplotlib>=1.5',
                          'numpy>=1.11',
                          'networkx>=1.10,<=1.11',
                          'pydotplus',
                          'pandas>=0.18',
                          'psutil>=3.0',
                          'errand_boy>=0.3',  # we want to get rid of this dependency eventually
                          'orderedset>=2.',
                          #'pyparsing==1.5.7',
                          'setproctitle>=1.1',
                          'sortedcontainers>=0.9'],
        ext_modules=[
            Extension(
                splitext(relpath(path, 'src').replace(os.sep, '.'))[0],
                sources=[path],
                include_dirs=( [dirname(path),cython_gsl.get_include(), cython_gsl.get_cython_include_dir(), numpy.get_include()]
                               if Cython else [dirname(path),cython_gsl.get_include(),numpy.get_include()] ),
                libraries = cython_gsl.get_libraries(),
                library_dirs=[cython_gsl.get_library_dir()],
                extra_compile_args = ["-O3", "-Wall", "-fopenmp"],
                extra_link_args = ['-g', '-fopenmp']
            )
            for root, _, _ in os.walk('src')
            for path in glob(join(root, '*.pyx' if Cython else '*.c'))
        ],
        scripts = [join('src','VirtualMicrobes','simulation','virtualmicrobes.py'),
                   join('src','VirtualMicrobes','simulation','start.py')],
        cmdclass = {'test': PyTest},
        extras_require={
            'testing': ['pytest'],
            },
        classifiers=[
            # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Cython',
            'Topic :: Scientific/Engineering :: Artificial Life',
            'Topic :: Scientific/Engineering',
        ],

    )

    os.chdir(curdir)
    if len(args):
        sys.argv = orig_sys_argv

if __name__ == "__main__":
    do_setup()
