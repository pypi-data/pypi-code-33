from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='manifestare',
    version='0.0.1',
    description='Simple, fluent, and descriptive API to explicit DataFrames expectations.',
    url='https://github.com/caique/manifestare',
    author='Caique Rodrigues',
    author_email='caiquepeixoto1@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='unit testing dataframe pandas spark',
    packages=find_packages(exclude=['contrib', 'docs', 'test']),
    python_requires='>=3.6',
    install_requires=['pyspark', 'pandas']
)
