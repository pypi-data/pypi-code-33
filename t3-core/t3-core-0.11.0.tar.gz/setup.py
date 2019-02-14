#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import setup, find_packages
import versioneer


here = os.path.abspath(os.path.dirname(__file__))

readme_file = os.path.join(here, 'README.md')
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        readme = f.read()

# get the dependencies and installs
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]
tests_require = []

setup(
    author="Travis Krause",
    author_email='travis.krause@t-3.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        "Operating System :: OS Independent",
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Boilerplate to quickly setup a Django Rest Framework Microservice for T3",
    long_description=readme,
    install_requires=install_requires,
    dependency_links=dependency_links,
    include_package_data=True,
    keywords='t3 t3-python-core',
    name='t3-core',
    packages=find_packages('./src'),
    package_dir={'': 'src'},
    test_suite='tests',
    tests_require=tests_require,
    url='https://www.t-3.com/',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # zip_safe=False,
)
