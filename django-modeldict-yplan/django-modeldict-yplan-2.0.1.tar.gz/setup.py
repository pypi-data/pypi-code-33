#!/usr/bin/env python
import os
import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename, 'r') as fp:
        contents = fp.read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)


version = get_version(os.path.join('modeldict', '__init__.py'))

with open('README.rst', 'r') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', 'r') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='django-modeldict-yplan',
    version=version,
    author='DISQUS',
    author_email='opensource@disqus.com',
    maintainer='Adam Johnson',
    maintainer_email='me@adamj.eu',
    url='https://github.com/adamchainz/django-modeldict',
    description='Stores a model as a dictionary',
    long_description=readme + '\n\n' + history,
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    license='Apache License 2.0',
    include_package_data=True,
    python_requires='>=3.4',
    install_requires=[
        'Django>=1.11',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
        'Topic :: Software Development'
    ],
)
