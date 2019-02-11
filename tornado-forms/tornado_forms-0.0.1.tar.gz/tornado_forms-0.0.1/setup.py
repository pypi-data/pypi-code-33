import os, json
from setuptools import setup, find_packages
from codecs import open

config = {
    "name": "tornado_forms",
    "version": "0.0.1",
    "description": "Build HTML forms from any data source in Tornado applications",
    "url": "https://github.com/tornadostack/tornado_forms",
    "author": "Sean Harrison",
    "author_email": "sah@bookgenesis.com",
    "classifiers": [
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3",
    ],
    "entry_points": {},
    "install_requires": [],
    "extras_require": {"dev": [], "test": []},
    "package_data": {},
    "data_files": [],
    "scripts": [],
}

path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'README.md'), encoding='utf-8') as f:
    read_me = f.read()

setup(
    long_description=read_me, packages=find_packages(exclude=['contrib', 'docs', 'tests']), **config
)
