#!/usr/bin/env python
from setuptools import setup
from quarksmart.settings import version_info

setup(
    name = 'quarksmart',
    description = 'Biblioteca para integração entre o Python e o sistema QuarkSmart.',
    version = ".".join([str(v) for v in version_info]),
    author = 'ESIG Software',
    author_email = 'contato@esig.com.br',
    packages = ['quarksmart'],
    keywords = 'data science quarksmart'
)

min_numpy_ver = '1.9.0'
setuptools_kwargs = {
    'install_requires': [
        'pandas >= 0.22.0',
        'numpy >= {numpy_ver}'.format(numpy_ver=min_numpy_ver),
    ],
    'setup_requires': ['numpy >= {numpy_ver}'.format(numpy_ver=min_numpy_ver)],
    'zip_safe': False,
}