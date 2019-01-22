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
    """Retrieves the version from django_darthmail/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("django_darthmail", "__init__.py")


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()

setup(
    name='django-darthmail',
    version=version,
    description="""Client for the DarthMail project""",
    long_description=readme,
    long_description_content_type='text/markdown',
    author='RegioHelden GmbH',
    author_email='entwicklung@regiohelden.de',
    url='https://github.com/regiohelden/django-darthmail',
    packages=[
        'django_darthmail',
    ],
    include_package_data=True,
    install_requires=[
        "django>=1.11",
        "requests[security]>=2.14.2",
        "six",
    ],
    extras_require={
        ":python_version<'3'": ["future>=0.16.0"]
    },
    license="BSD",
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Email',
    ],
)
