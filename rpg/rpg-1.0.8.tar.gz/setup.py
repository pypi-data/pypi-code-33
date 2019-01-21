# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

_MAJOR = 1
_MINOR = 0
_MICRO = 8
version = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release = '%d.%d' % (_MAJOR, _MINOR)

metainfo = {
    'authors': {
        'Maillet': ('Nicolas Maillet', 'nicolas.maillet@pasteur.fr'),
        },
    'version': version,
    'license': 'GPLv3',
    'description': 'In silico protein digestion',
    'platforms': ['Linux', 'Unix', 'MacOsX', 'Windows'],
    "keywords": ["protein", "peptide", "enzyme", "protease", "digestion"],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',]
    }


with open('README.rst') as f:
    readme = f.read()

requirements = open("requirements.txt").read().split()

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    # mock, pillow, sphinx, sphinx_rtd_theme installed on RTD
    # but we also need numpydoc and sphinx_gallery
    extra_packages = ["numpydoc", "sphinx_gallery"]
    requirements += extra_packages


setup(
    name='rpg',
    version=version,
    maintainer=metainfo['authors']['Maillet'][0],
    maintainer_email=metainfo['authors']['Maillet'][1],
    author='Nicolas Maillet',
    author_email=metainfo['authors']['Maillet'][1],
    long_description=readme,
    keywords=metainfo['keywords'],
    description=metainfo['description'],
    license=metainfo['license'],
    platforms=metainfo['platforms'],
    classifiers=metainfo['classifiers'],
    zip_safe=False,
    packages=find_packages(),
    install_requires=requirements,

    # This is recursive include of data files
    exclude_package_data={"": ["__pycache__"]},
    # Command line
    entry_points={
        'console_scripts': [
            'rpg=rpg.RapidPeptidesGenerator:main'
        ]
    }
)
