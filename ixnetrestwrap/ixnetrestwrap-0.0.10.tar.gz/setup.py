import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ixnetrestwrap",
    version="0.0.10",
    author="Parthiban Ramachandran",
    author_email="rparthibaan@gmail.com",
    description="Rest API Wrapper For IxNetwork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ParthibanRamachandran/IxNetwork/tree/master/RestApi/Python/Modules",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
