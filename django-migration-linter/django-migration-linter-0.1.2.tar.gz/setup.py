# Copyright 2019 3YOURMIND GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import ast
import re
from os import path
from setuptools import setup, find_packages


PROJECT_DIR = path.abspath(path.dirname(__file__))


def get_version():
    constants = path.join(PROJECT_DIR, 'django_migration_linter', 'constants.py')
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(constants, "r") as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


with open(path.join(PROJECT_DIR, 'README.rst')) as f:
    long_description = f.read()

install_requirements = [
    'django>=1.11',
    'appdirs==1.4.3'
]

test_requirements = [
    'pytest',
    'tox',
    'django-fake-database-backends',
]

# noinspection PyUnresolvedReferences
setup(
    name='django-migration-linter',
    version=get_version(),

    description='Detect backward incompatible migrations for your django project',
    long_description=long_description,
    url='https://github.com/3YOURMIND/django-migration-linter',
    author='3YOURMIND GmbH',
    license='Apache License 2.0',

    packages=find_packages(exclude=['tests/']),
    install_requires=install_requirements,
    extras_require={
        'test': test_requirements
    },
    entry_points={
        'console_scripts': [
            'django-migration-linter = django_migration_linter.migration_linter:_main'
        ]
    },

    keywords='django migration lint linter database backward compatibility',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
