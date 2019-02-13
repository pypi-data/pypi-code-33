#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function,
)

import io
import os
import re
import sys
from glob import glob
from os.path import (
    basename,
    dirname,
    join,
    relpath,
    splitext,
)

from setuptools import (
    Extension,
    find_packages,
    setup,
)

try:
    # Allow installing package without any Cython available. This
    # assumes you are going to include the .c files in your sdist.
    from Cython.Distutils import build_ext
except ImportError:
    from setuptools.command.build_ext import build_ext


class CustomBuildExtCommand(build_ext):
    """build_ext command for use when pysam headers/libraries are needed."""

    def run(self):  # noqa: D102

        # Import pysam here, only when headers are needed
        import pysam

        # Add pysam headers to include_dirs
        self.include_dirs.extend(pysam.get_include())
        if sys.platform == 'darwin':
            self.extra_link_args = ['-Wl,-rpath,%s' % os.path.relpath(pysam.get_include()[0])]

        # Call original build_ext command
        build_ext.run(self)


def read(*names, **kwargs):  # noqa: D103
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


# Enable code coverage for C code: we can't use CFLAGS=-coverage in tox.ini, since that may mess with compiling
# dependencies (e.g. numpy). Therefore we set SETUPPY_CFLAGS=-coverage in tox.ini and copy it to CFLAGS here (after
# deps have been safely installed).
if 'TOXENV' in os.environ and 'SETUPPY_CFLAGS' in os.environ:
    os.environ['CFLAGS'] = os.environ['SETUPPY_CFLAGS']

setup(
    name='compare-reads',
    version='0.0.0',
    license='MIT license',
    description='cythonized function to compare reads by name',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Marius van den Beek',
    author_email='m.vandenbeek@gmail.com',
    url='https://github.com/mvdbeek/pysam-compare-reads',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://pysam-compare-reads.readthedocs.io/',
        'Changelog': 'https://pysam-compare-reads.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/mvdbeek/pysam-compare-reads/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=[
        'pysam',
    ],
    setup_requires=[
        'Cython',
        'pysam'
    ],
    cmdclass={'build_ext': CustomBuildExtCommand},
    ext_modules=[
        Extension(
            splitext(relpath(path, 'src').replace(os.sep, '.'))[0],
            sources=[path],
            include_dirs=[dirname(path)],
        )
        for root, _, _ in os.walk('src')
        for path in glob(join(root, '*.pyx'))
    ],
)
