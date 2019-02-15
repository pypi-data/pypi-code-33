# -*- coding:utf-8 -*-

import setuptools
#
# with open("README.md", "r") as fh:
#     long_description = fh.read()


setuptools.setup(
    name="krust",
    version="0.0.9",
    author="claydodo and his little friends (xiao huo ban)",
    author_email="claydodo@foxmail.com",
    description="Shell utils",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/claydodo/krust",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7 ",
        "Programming Language :: Python :: 3 ",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'krux >= 0.0.10'
    ]
)
