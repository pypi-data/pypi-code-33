#!/usr/bin/env python

from setuptools import setup

long_desc = open('README.md').read()

setup(name='alarmdealerscrape',
    version='1.0.2',
    description='scraper for alarmdealer.com',
    long_description=long_desc,
    py_modules=('alarmdealerscrape',),
    install_requires=[
        'beautifulsoup4',
        'requests>=2.2',
        'websocket-client>=0.44',
    ],
    license='BSD',
    author='Ryan Nowakowski',
    author_email='tubaman@fattuba.com',
    url='https://github.com/tubaman/alarmdealerscrape',
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries',
    )
)
