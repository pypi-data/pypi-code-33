from os import path
from setuptools import setup


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'r') as f:
    long_description = f.read()


setup(
    name='icelander_generator',
    packages=['icelander_generator'], # this must be the same as the name above
    version='0.3.1',
    description='A utility to generate random Icelanders',
    author='7oi',
    author_email='7oi@7oi.is',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/7oi/IcelanderGenerator',
    install_requires=[
        'lxml',
        'requests',
        'kennitala',
        'future'
    ],
    include_package_data=True,
    keywords=['tests', 'generator'],
    classifiers = [],
)
