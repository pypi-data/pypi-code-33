# coding: utf8
# Author:xuyang.li
# Date:2018/11/20
"""
    Install to PIP
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enos-api-sdk-python",
    version="0.0.2",
    author="lihu.yang",
    author_email="lihu.yang@envision-digital.com",
    description="EnOS API SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EnvisionIot/enos-api-sdk-python.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyOpenSSL==18.0.0',
        'poster==0.8.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
    ],
)
