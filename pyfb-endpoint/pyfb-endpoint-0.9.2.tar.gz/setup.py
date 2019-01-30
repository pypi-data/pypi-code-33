#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from pyfb_endpoint/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("pyfb_endpoint", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pyfb-endpoint',
    version=version,
    description="""Endpoint app for PyFreeBilling""",
    long_description=readme + '\n\n' + history,
    author='Mathias WOLFF',
    author_email='mathias@celea.org',
    url='https://github.com/mwolff44/pyfb-endpoint',
    packages=[
        'pyfb_endpoint',
    ],
    include_package_data=True,
    install_requires=[
        "django-model-utils>=3.1.2",
        "django-extensions>=2.1.3",
        "djangorestframework>=3.9.0",
        "django-crispy-forms>=1.7.0",
        "pyfb-company>=0.9.0",
        "pyfb-normalization>=1.0.0",
        "psycopg2>=2.7.4",
        "django-partial-index>=0.5.2",
        "django-migrate-sql-deux>=0.2.1",
        "django-autocomplete-light>=3.3.2",
        "netaddr>=0.7.19",
    ],
    license="MIT",
    zip_safe=False,
    keywords='pyfb-endpoint',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
