"""
Setup script for roles module.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from contextlib import closing
import glob

VERSION = '0.1'

with closing(open('README.txt')) as f:
    doc = f.read()

setup(
    name='py_roles',
    version=VERSION,
    description='Role based development',
    long_description=doc,
    author='Leonid Soputnyak',
    author_email='leonid.soputnyak@gmail.com',
    license="BSD License",
    packages=['roles'],
    keywords="role DCI data context interaction",
    platforms=["All"],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development :: Libraries']
)
