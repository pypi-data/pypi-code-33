#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

PACKAGE = 'metabeyond'

# These are added by CI automatically.
__version__ = "0.2.1"


# Fill in manually if required in the future.
__requirements__ = []
__author__ = "flitt3r"
__license__ = "MIT"


# Used by CI, fill in manually...
__deploy_requirements__ = ['twine', 'black', 'wheel', 'setuptools']
__test_requirements__ = ['coverage', 'asynctest']
__sast_requirements__ = ['bandit']
__docs_requirements__ = [
    'sphinx',
    'graphviz',
    'Jinja2',
    'solar-theme',
    'sphinxcontrib-fulltoc',
    'sphinx-autodoc-typehints',
    'sphinxcontrib-asyncio',
]


# Only works when building, not installing...
try:
    with open('README.md') as fp:
        print('Read in the README')
        readme_content = fp.read()
    readme_content_type = 'text/markdown'
except Exception:
    readme_content = 'Visit the GitLab repo for more details'
    readme_content_type = 'text/plain'


# Decent reference:
# https://gemfury.com/stevenferreira/python:sample/-/content/setup.py?gclid=Cj0KCQiApILhBRD1ARIsAOXWTztNWw_wmu2xA4Ka0yn-EjwbS99NZBI19Pjozfw7qAjVGSXDTY6grkkaAm1WEALw_wcB
setup(
    name=PACKAGE,
    version=__version__,
    description="Metadata for Python",
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Development Status :: 1 - Planning
        # Development Status :: 2 - Pre-Alpha
        # Development Status :: 3 - Alpha
        # Development Status :: 4 - Beta
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='Metadata Java 6 annotation @interface hint documentation',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=__requirements__,
    extras_require={
        'test': __test_requirements__,
        'sast': __sast_requirements__,
        'docs': __docs_requirements__,
        'deploy': __deploy_requirements__,
        'develop': __requirements__,
    },
    include_package_data=True,
    python_requires='>=3.6.0',
    long_description=readme_content,
    long_description_content_type=readme_content_type,
)
