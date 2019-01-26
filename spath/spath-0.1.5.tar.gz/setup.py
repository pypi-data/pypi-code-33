#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

version = '0.1.5'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'six',
    'path.py',
    'humanize',
    'pillow',
]

# suggested: numpy, cv2, ...

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='spath',
    version=version,
    description="Extras for path.py",
    long_description=readme + '\n\n' + history,
    author="Daniel Maturana",
    author_email='dimatura@cmu.edu',
    url='https://github.com/dimatura/spath.py',
    download_url = 'https://github.com/dimatura/spath.py/tarball/%s.zip' % version,
    packages=[
        'spath',
    ],
    package_dir={'spath':
                 'spath'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='spath',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
