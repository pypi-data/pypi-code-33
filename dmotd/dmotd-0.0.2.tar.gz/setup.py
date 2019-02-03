# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from setuptools import setup

def get_file_conts(file):
    with open(file, "r") as f:
        contents = f.read()
    
    return contents

setup(
    name="dmotd",
    version="0.0.2",
    description="Dynamic Message Of The Day.",
    long_description=get_file_conts("README.md"),
    long_description_content_type="text/markdown",
    url="http://github.com/monolix/dmotd",
    author="Monolix",
    author_email="monolix.team@gmail.com",
    license="MIT",
    packages=["dmotd"],
    install_requires=get_file_conts("requirements.txt").split("\n"),
    zip_safe=False
)