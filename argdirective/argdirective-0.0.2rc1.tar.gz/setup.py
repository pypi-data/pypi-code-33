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
    name='argdirective', 
    version='0.0.2rc1', 
    description='Argdirective is a python module to detect the first command line argument as subcommand.', 
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/domsonAut/argdirective',
    author='Dominik Kummer',
    author_email='admin@arkades.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='shell argument directive',
    py_modules=["generator"],
    python_requires='>=3',
    install_requires=['builtins', 'argparse', 'pkgutil', 'imp', 'pprint', 'logging'],
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/domsonAut/argdirective/issues',
        'Source': 'https://gitlab.com/domsonAut/argdirective/',
    },
)
