import os
import sys
from setuptools import setup, find_packages

PACKAGE_NAME = 'd3m'
MINIMUM_PYTHON_VERSION = 3, 6


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {}.{}+ is required.".format(*MINIMUM_PYTHON_VERSION))


def read_package_variable(key):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, '__init__.py')
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ')
            if parts and parts[0] == key:
                return parts[-1].strip("'")
    raise KeyError("'{0}' not found in '{1}'".format(key, module_path))


check_python_version()
version = read_package_variable('__version__')
description = read_package_variable('__version__')
author = read_package_variable('__version__')

setup(
    name=PACKAGE_NAME,
    version=version,
    description=version,
    author=author,
    packages=find_packages(exclude=['contrib', 'docs', 'site', 'tests*']),
    package_data={'d3m': ['metadata/schemas/*/*.json']},
    install_requires=[
        'scikit-learn[alldeps]==0.20.2',
        'pytypes==1.0b5',
        'frozendict==1.2',
        'numpy==1.15.4',
        'jsonschema==2.6.0',
        'requests==2.19.1',
        'strict-rfc3339==0.7',
        'rfc3987==1.3.8',
        'webcolors==1.8.1',
        'dateparser==0.7.0',
        'pandas==0.23.4',
        'networkx==2.2',
        'typing-inspect==0.3.1',
        'GitPython==2.1.11',
        'jsonpath-ng==1.4.3',
        'custom-inherit==2.2.0',
        'PyYAML==3.13',
        'pycurl==7.43.0.2',
        'pyarrow==0.11.1',
        'gputil==1.3.0',
    ],
    tests_require=[
        'docker[tls]==2.7',
    ],
    url='https://gitlab.com/datadrivendiscovery/d3m',
)
