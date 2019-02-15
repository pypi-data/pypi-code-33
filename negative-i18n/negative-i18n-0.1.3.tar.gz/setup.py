#!/usr/bin/env python

import os
import sys
from glob import glob

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://negative-i18n.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def find_package_data(*allowed_extensions):
    package_data = {}

    for ext in allowed_extensions:
        for file in glob(f'**/*.{ext}', recursive=True):
            pos = -1
            parts = file.split('/')
            while True:
                prefix = '/'.join(parts[0:pos])
                package = '.'.join(parts[0:pos])
                data_file = '/'.join(parts[pos:])

                if prefix == '':
                    break

                if os.path.exists(os.path.join(prefix, '__init__.py')):
                    break

                pos -= 1

            if prefix != '':
                if package not in package_data:
                    package_data[package] = []

                package_data[package].append(data_file)

    return package_data



setup(
    name='negative-i18n',
    version='0.1.3',
    description='Database-stored translation strings for Django',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    url='https://github.com/negative-space/negative-i18n',
    packages=[
        'negative_i18n',
        'negative_i18n.migrations',
        'negative_i18n.templatetags',
    ],
    package_data=find_package_data('js', 'css', 'html'),
    package_dir={'negative_i18n': 'negative_i18n'},
    # include_package_data=True,
    install_requires=[
        'django-modeltranslation>=0.13b',
        'polib',
        'django>=2.0',
    ],
    license='MIT',
    zip_safe=False,
    keywords='negative-i18n',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
