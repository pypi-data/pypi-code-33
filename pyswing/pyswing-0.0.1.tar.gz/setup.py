import setuptools

import pyswing

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pyswing",
    version=pyswing.__version__,
    author="Jorge Fernández Sánchez",
    author_email="jfsanchez.email@gmail.com",
    description="PySwing is a REST (Representational State Transfer) load-balancer service.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zonnesoft/pyswing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
