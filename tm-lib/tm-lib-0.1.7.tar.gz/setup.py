from setuptools import setup, find_packages
from os import path

from io import open

from tmlib import VERSION

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt") as install_requires_file:
    install_requires = install_requires_file.readlines()

setup(
    name='tm-lib',  # Required
    version=VERSION,  # Required
    description='A lib for the tm projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/trading-minions/prototypes/tmlib',
    author='Michael Smith',
    author_email='mike@tradingminions.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='tmlib',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=install_requires,
    extras_require={
        'dev': ['ipdb'],
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
)
