""" Setup script. Used by easy_install and pip. """

import os
import sys
import subprocess as sp
import re

from setuptools import setup, find_packages, Command

VERSIONFILE="extasycoco/_version.py"
name="extasycoco"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))

#-----------------------------------------------------------------------------
# check python version. we need > 2.5
if  sys.hexversion < 0x02050000:
    raise RuntimeError("%s requires Python 2.5 or higher" % name)


#-----------------------------------------------------------------------------
#
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


#-----------------------------------------------------------------------------
setup_args = {
    'name'             : "extasycoco",
    'version'          : verstr,
    'description'      : "EXTASY Project - Coco",
    'long_description' : (read('README.md') + '\n\n' + read('CHANGES.md')),
    'author'           : "The EXTASY Project",
    'url'              : "https://bitbucket.org/extasy-project/extasy-project",
    'download_url'     : "https://bitbucket.org/extasy-project/coco/get/"+verstr+".tar.gz",
    'license'          : "BSD",
    'classifiers'      : [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'packages'    : find_packages(),
    'scripts' : ['scripts/pyCoCo'],
    'install_requires' : ['numpy',
                          'scipy',
                          'scikit-image',
                          'pypcazip>=1.5.6',
                          'mdtraj'],
    'zip_safe'         : False,
}

#-----------------------------------------------------------------------------

setup (**setup_args)
