#!/usr/bin/env python3

from setuptools import setup

readme = open('README.md').read()

setup(
    name = 'wolphin-driver',
    version = '0.0.4',
    description = "Docker custom base directory volume driver",
    long_description = readme,
    long_description_content_type='text/markdown',
    author = "Wolphin",
    author_email = "wolphin@wolph.in",
    url = "https://gitlab.com/q_wolphin/wolphin-driver",
    packages = ['wolphin_driver'],
    classifiers = [
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=[
        'flask',
        'gunicorn',
        'envparse'
    ],
    entry_points={
        'console_scripts': [
            'wolphin-driver=wolphin_driver.main:main',
        ]
    },
)

