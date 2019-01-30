from setuptools import setup, find_packages
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md')) as f:
    long_description = f.read()

setup(
    name='my_project',
    author='author',
    author_email='author_email',
    url='repository_url',
    version='1.0',
    description="description",
    long_description=long_description,
    packages=find_packages(),
)
