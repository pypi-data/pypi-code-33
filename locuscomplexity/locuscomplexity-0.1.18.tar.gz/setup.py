from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='locuscomplexity',
    version='0.1.18',
    packages=['locuscomplexity'],
    url='https://github.com/LocusAnalytics/EconCmplx',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'pandas', 'networkx', 'matplotlib',],
    test_suite='nose.collector',
    tests_require=['nose'],
    package_data={
        './': ['*.pkl'],
    },
)
