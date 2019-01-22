#!/usr/bin/env python

import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()

dependency_link_urls = filter(
    lambda x: x.startswith('-e'),
    required
)

# Installations from git repositories must be specified via
# dependency links. Try to convert the URLs to GIT archive links
# in a very naive way
dependency_links = []
for dependency_link_url in dependency_link_urls:
    required.remove(dependency_link_url)
    egg = dependency_link_url.split('#')[-1].split('=')[-1]
    required.append(''.join(reversed('=='.join(''.join(reversed(egg)).split('-', 1)))))
    dependency_links.append(
        re.sub(r'^-e ((git|http|https)+?)+://', 'https://', dependency_link_url)
            .replace('.git@', '/tarball/')
    )

setup(
    name='geographica-longitude-async',

    version='0.3.39',

    description='Longitude',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url='https://github.com/GeographicaGS/Longitude-async',

    # Author details
    author='Geographica',
    author_email='pypi@geographica.gs',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    # What does your project relate to?
    keywords='carto longitude alembic async sanic jwt',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[required],
    dependency_links=dependency_links,

    entry_points={
        'console_scripts': [
            'lmigrate = longitude.migration.command:main'
        ]
    }
)
