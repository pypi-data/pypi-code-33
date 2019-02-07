
from setuptools import setup, find_packages


with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='basicsums',
    version='1.0.1',
    author='Wojciech Nawalaniec',
    author_email='wnawalaniec@gmail.com',
    packages=find_packages(),   
    url='http://basicsums.bitbucket.io/',
    license='LICENSE.txt',
    description=('A package for computing structural sums'
		 ' and the effective conductivity of random composites.'),
    long_description=long_description,
    package_data={'basicsums': ['examples/data/*.npz']},
    install_requires=[
        "numpy>=1.14.0",
        "matplotlib>=2.1.2",
	"sympy>=1.1.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
