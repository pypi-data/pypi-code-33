from setuptools import setup, find_packages

long_description = """
# threadLRU
Thread-Safe LRU Cache in Python
[![Build Status](https://travis-ci.com/mattpaletta/pqdict.svg?branch=master)](https://travis-ci.com/mattpaletta/pqdict)

## Instalation
Thread LRU has no external dependencies.
To install threadlru:
```
pip install threadlru
```
"""

setup(
    name="threadlru",
    version="0.0.1",
    url='https://github.com/mattpaletta/threadlru',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    setup_requires=[],
    author="Matthew Paletta",
    author_email="mattpaletta@gmail.com",
    description="Thread-Safe LRU Implementation",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    license="GNU GPLv3",
    python_requires='>=3.6',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Natural Language :: English",
    ]
)