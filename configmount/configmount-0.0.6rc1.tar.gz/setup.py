"""A setuptools based setup module for configmount.
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='configmount', 
    version='0.0.6rc1', 
    description='Configmount mounts directories containing configuration files (augtools compatible files, yaml-files) as directories, so that every configuration value is accessible as file.', 
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/domsonAut/configmount',
    author='Dominik Kummer',
    author_email='admin@arkades.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='filesystem oriented configuration management',
    py_modules=["data", "mount", "operations"],
    python_requires='>=3',
    install_requires=['argdirective', 'python-augeas', 'PyYAML', 'dpath', 'lockfile', 'llfuse', 'xattr'],
    scripts=['scripts/configmount'],
    project_urls={
        'Bug Reports': 'https://gitlab.com/domsonAut/configmount/issues',
        'Source': 'https://gitlab.com/domsonAut/configmount/',
    },
)
