# setup.py is the build script for setuptools

"""
Author: kidzying
Mail: kidzying@163.com
Created Time:  2019-01-30
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


PACKAGES=['data_overview']

setuptools.setup(
    name="data_overview",
    version="0.1.0",
    author="kidzying",
    author_email="kidzying@163.com",
    description="数据表概览-数据分析第一步",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://blog.duanzhiying.com",
    packages=PACKAGES,
    include_package_data = True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas"]
)