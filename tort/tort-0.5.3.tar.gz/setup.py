#!/usr/bin/env python
from setuptools import setup

kwargs = {}

with open('tort/version.py') as f:
    ns = {}
    exec(f.read(), ns)
    version = ns['version']

install_requires = ['tornado >= 6.0a1']


with open('README.rst') as f:
    kwargs['long_description'] = f.read()


python_requires = '>= 3.7'
kwargs['python_requires'] = python_requires

setup(
    name='tort',
    version=version,
    description='Tort - Tornado framework helper functions',
    url='https://github.com/glibin/tort',
    download_url='https://github.com/glibin/tort/tarball/{}'.format(version),
    packages=['tort', 'tort.test', 'tort.util'],
    install_requires=install_requires,
    long_description_content_type='text/x-rst',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    **kwargs
)
