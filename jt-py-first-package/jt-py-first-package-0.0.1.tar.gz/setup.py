"""
jt-py-first-package Python package is for Joe Tilsed to learn how to write a python package and
upload it onto PyPi. Also to show and teach others how to do it themselves.
---
setup.py is the build script for setuptools.
It tells setuptools about your package (such as the name and version) as well as which code files to include.
"""

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='jt-py-first-package',
    version="0.0.1",
    author="Joe Tilsed",
    author_email="Joe@Tilsed.com",
    description="Learning how to create and deploy my own python packages onto PyPi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/tilsedtowers/jt-py-first-package/src",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)


# That's all folks...
