#!/usr/bin/env python
#-*- coding:utf-8 -*-


from setuptools import setup, find_packages

setup(
    name = "search-engine",
    version = "0.0.6",
    keywords = ("search", "myvyang"),
    description = "fetch search engine result",
    long_description = "fetch search engine result",
    license = "MIT Licence",

    url = "https://github.com/myvyang/search_engine",
    author = "myvyang",
    author_email = "myvyang@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [
         "requests",
        "six",
        "beautifulsoup4"
    ]
)
