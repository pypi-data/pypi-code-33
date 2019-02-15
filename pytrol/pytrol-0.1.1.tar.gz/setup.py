import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytrol",
    version="0.1.1",
    author="daehruoydeef (Oskar)",
    author_email="author@nodata.com",
    description="easy to use Linux process managment in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daehruoydeef/pytrol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
