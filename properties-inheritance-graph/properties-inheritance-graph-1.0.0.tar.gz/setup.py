#!/usr/bin/env python
"""properties-inheritance-graph: Make graphs of HasProperties class networks"""

import setuptools

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS',
    'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setuptools.setup(
    name='properties-inheritance-graph',
    version='1.0.0',
    packages=setuptools.find_packages(exclude=('tests',)),
    install_requires=[
        'properties',
        'networkx',
    ],
    author='Seequent',
    author_email='franklin.koch@seequent.com',
    description='Make graphs of HasProperties class networks',
    long_description=LONG_DESCRIPTION,
    keywords='networkx, properties, graph',
    url='https://github.com/seequent/properties-inheritance-graph',
    classifiers=CLASSIFIERS,
    platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    use_2to3=False,
)
