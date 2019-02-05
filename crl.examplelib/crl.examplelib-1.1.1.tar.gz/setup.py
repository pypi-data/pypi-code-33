__copyright__ = 'Copyright (C) 2019, Nokia'

import os
import imp
from setuptools import setup, find_packages


VERSIONFILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'src', 'crl', 'examplelib', '_version.py')


def get_version():
    return imp.load_source('_version', VERSIONFILE).get_version()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='crl.examplelib',
    version=get_version(),
    author='Petri Huovinen',
    author_email='petri.huovinen@nokia.com',
    description='Example of Common Robot Library',
    install_requires=[],
    long_description=read('README.rst'),
    license='BSD-3-Clause',
    keywords='robotframework, example',
    url='https://github.com/nokia/crl-examplelib',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['crl'],
    entry_points={'robotdocsconf': [
        'robotdocsconf = crl.examplelib.robotdocsconf:robotdocs']},
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ],
)
