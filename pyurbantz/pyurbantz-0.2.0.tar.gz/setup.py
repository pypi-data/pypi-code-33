#!/usr/bin/env python3
from setuptools import setup, find_packages


def read_requirements(filename):
    return [req.strip() for req in open(filename)]


setup(
    name='pyurbantz',
    version=open('VERSION').read().strip(),
    author='Lucidiot',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={
        '': ['*.md', 'LICENSE', 'README'],
    },
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
    },
    license='GNU General Public License 3',
    description="A helper for UrbanTZ's public undocumented API",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords="api urbantz order delivery tracking",
    url="https://gitlab.com/Lucidiot/pyurbantz",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    project_urls={
        "Source Code": "https://gitlab.com/Lucidiot/pyurbantz",
        "GitHub Mirror": "https://github.com/Lucidiot/pyurbantz",
    }
)
