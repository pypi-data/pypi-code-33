#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='SearchEngineSpider',
    version='0.1.1',
    description="A search engine spider",
    install_requires=['pyquery>=1.2.17', 'requests>=2.12.4', 'cchardet', 'zcommand', 'bs4'],
    author='izhengzhixian',
    author_email='izhengzhixian@gmail.com',
    platforms='any',
    packages=find_packages(),
    package_data={'search_engine_spider': ['data/*.txt'], 'search_engine_spider.search_engine': ['data/*.txt']},
    scripts=['bin/search_engine_spider'],
)
