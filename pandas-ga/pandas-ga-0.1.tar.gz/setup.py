import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pandas-ga",
    version="0.1",
    author="Connell Blackett",
    description="Reading Google Analytics report into Pandas dataframe",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/connellblackett/pandas-ga",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)