"""Satsense package."""
from setuptools import find_packages, setup

with open('README.md') as file:
    README = file.read()

with open('rcm/_version.py') as file:
    for line in file:
        line = line.strip()
        if line.startswith('__version__'):
            VERSION = line.split('=')[1].strip(' "').strip("'")
            break

setup(
    name='rcm',
    version=VERSION,
    url='https://gitlab.computationalscience.nl/dynaslum/residential-choice-model',
    license='Apache Software License',
    author='Berend Weel, Debraj Roy',
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest', 'pytest-cov',
        'pytest-flake8', 'pytest-html'
    ],
    install_requires=[
        'shapely',
        'pyproj',
        'osmnx',
        'numpy',
        'Mesa',
        'mesa-geo',
    ],
    extras_require={
        'dev': [
            'isort',
            'pycodestyle',
            'pyflakes',
            'pytest',
            'pytest-cov',
            'pytest-flake8',
            'pytest-html',
        ],
        'notebooks': [
            'jupyter',
            'matplotlib',
            'nblint',
        ],
    },
    author_email='b.weel@esiencecenter.nl',
    description=('Library for geo-spatial multi-agent models.'),
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])
