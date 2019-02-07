#!/usr/bin/env python
from setuptools import setup, find_packages
name = "slogger"

requires = ['fn==0.4.3']

setup(
    name = name,
    version = '1.2.1',
    author = 'Zongying Cao',
    author_email = 'zongying.cao@dxc.com',
    description = 'slogger is a dead simple logger to use. It can be configured in very easy way.',
    long_description = """slogger is not simple wrapper for pythong logging module. It easy to use and configure""",
    packages = [name],
    url = "https://github.com/cao5zy/slogger",
    package_dir = {'slogger': 'slogger'},
    package_data = {'slogger': ["*.py"]},
    include_package_data = True,
    install_requires = requires,
    license = 'MIT',
    classifiers = [
               'Development Status :: 4 - Beta',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: Apache Software License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development :: Libraries',
           ],
)
