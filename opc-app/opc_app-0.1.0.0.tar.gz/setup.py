#!/usr/bin/env python
import sys
from setuptools import setup
import io

from os import path
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='opc_app',
    version='0.1.0.0',
    description='API that communicates with KEP server for XMPro demo machine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kevin Glasson',
    author_email='kevinglasson+timetable_tool@gmail.com',
    url='https://github.com/kevinglasson/TimetableTool.git',
    packages=['opc_app'],
    scripts=['bin/xmpro-demo-server'],
    install_requires=[
        'astroid==1.6.5', 'autopep8==1.4', 'backports.functools-lru-cache==1.5', 'click==6.7', 'configparser==3.5.0', 'enum34==1.1.6', 'Flask==1.0.2', 'futures==3.2.0', 'isort==4.3.4', 'itsdangerous==0.24', 'Jinja2==2.10', 'lazy-object-proxy==1.3.1', 'MarkupSafe==1.0', 'mccabe==0.6.1', 'pycodestyle==2.4.0', 'pydotenv==0.0.7', 'pylint==1.9.3', 'singledispatch==3.4.0.3', 'six==1.11.0', 'waitress==1.1.0', 'Werkzeug==0.14.1', 'wrapt==1.10.11'
    ],
    python_requires='==2.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7'
    ]
)
