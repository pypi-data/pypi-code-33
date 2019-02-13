# Copyright (C) 2012-2014 Kapiche Limited
# Author: Ryan Stuart <ryan@kapiche.com>
from setuptools import setup

# Use README.md as long_description
with open('README.rst') as f:
    long_description = f.read()

requires = [
    'apsw',
    'arrow',
    'nltk>=3.0',
    'regex'
]

setup(
    name='caterpillar',
    use_scm_version=True,
    long_description=long_description,
    packages=[
        'caterpillar',
        'caterpillar.processing',
        'caterpillar.processing.analysis',
        'caterpillar.resources',
        'caterpillar.storage',
    ],
    package_data={
        'caterpillar': ['resources/*.txt', 'VERSION'],
    },
    url='https://github.com/Kapiche/caterpillar',
    license='AGPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Indexing',
    ],
    keywords='indexing text analytics',
    install_requires=requires,
    setup_requires=['setuptools_scm'],
    extras_require={
        'test': ['tox', 'pytest', 'pytest-cov', 'coverage', 'pep8', 'mock'],
    },
    author='Kapiche',
    author_email='contact@kapiche.com',
    description='Text retrieval and analytics engine.'
)
