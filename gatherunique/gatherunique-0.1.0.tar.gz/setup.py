import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gatherunique",
    version="0.1.0",
    author="Daniel Paz Avalos",
    author_email="dpazavalos@protonmail.com",
    description="Simple, unique list gatherer, with *args for passable blacklist check and "
    "optional list_in for automated sorting against blacklist/s",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dpazavalos/datatypes/tree/master/gatherunique",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)