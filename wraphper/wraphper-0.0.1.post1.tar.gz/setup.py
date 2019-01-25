import setuptools
from wraphper import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wraphper",
    version=__version__,
    author="Aalaap Ghag",
    description="Python wrappers for PHP functions, when you just can't shake it.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aalaap/wraphper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: PHP",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)