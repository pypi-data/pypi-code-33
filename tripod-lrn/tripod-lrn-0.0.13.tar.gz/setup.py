# -*- coding: utf-8 -*-
"""
setup.py
------------
The Lib build script.
"""
from setuptools import setup, find_packages
# builds the project dependency list
install_requires = None
with open('requirements.txt', 'r') as f:
    install_requires = f.readlines()

# setup function call
setup(
    name="tripod-lrn",
    version="0.0.13",
    author="Luis Felipe Muller",
    author_email="luisfmuller@gmail.com",
    description=("Utility project code."),
    keywords="",
    # Install project dependencies
    install_requires=install_requires,

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md', "*.json", "*.zip"],
    },
    include_package_data=True,
    packages=find_packages(exclude=["*tests"]),
    entry_points={
        'console_scripts': ['tripod = tripod.main:main.run']
    }
)
