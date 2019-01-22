#!/usr/bin/env python

from setuptools import setup, find_packages

desc = ''
with open('README.rst') as f:
    desc = f.read()

setup(
    name='newrelic-extensions',
    version='0.1.0',
    description='Unofficial set of extensions for the NewRelic Python Agent',
    long_description=desc,
    url='https://github.com/jmvrbanac/python-newrelic-extensions',
    author='John Vrbanac',
    author_email='john.vrbanac@linux.com',
    license='Apache v2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='newrelic extensions',
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    python_requires='>=3.5',
    install_requires=[
        'newrelic>=4.10.0.112',
        'pike>=0.1.1',
    ],
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [],
    },
)
