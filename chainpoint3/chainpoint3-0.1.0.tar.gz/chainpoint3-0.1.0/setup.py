import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
install_requires = [
    "merkletools"
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='chainpoint3',
    version='0.1.0',
    description='Chainpoint proof of existence library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    url='https://github.com/GitTiago/pychainpoint',
    author='Tiago Santos',
    keywords='proof of existence, blockchain, merkle tree',
    license="MIT",
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=install_requires
)
