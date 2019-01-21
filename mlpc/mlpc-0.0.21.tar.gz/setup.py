import setuptools
from mlpc.metadata import MLPC_VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlpc",
    version=MLPC_VERSION,
    author="Snorre Visnes",
    author_email="snorre.visnes+mlpc@gmail.com",
    description="A python beginners attempt at a micro framework for ML projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tbd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)