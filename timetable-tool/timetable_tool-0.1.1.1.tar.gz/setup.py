#!/usr/bin/env python
import sys
from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='timetable_tool',
    version='0.1.1.1',
    description='Scrape a curtin timetable_tool into google calendar',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kevin Glasson',
    author_email='kevinglasson+timetable_tool@gmail.com',
    url='https://github.com/kevinglasson/TimetableTool.git',
    packages=['timetable_tool'],
    scripts=['bin/timetable-tool'],
    install_requires=[
        'beautifulsoup4==4.6.0', 'certifi==2018.11.29', 'chardet==3.0.4', 'google-api-python-client==1.6.2', 'httplib2==0.10.3', 'idna==2.5', 'lxml==4.1.1', 'oauth2client==4.1.3', 'pyasn1==0.4.5', 'pyasn1-modules==0.2.4', 'requests==2.21.0', 'rsa==4.0', 'six==1.12.0', 'uritemplate==3.0.0', 'urllib3==1.22'
    ],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ]
)
