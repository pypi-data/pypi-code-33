import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="batquant",
    version="0.0.4",
    author="Ninh Chu",
    author_email="chulucninh09@gmail.com",
    description="A package to get Vietnamese stock data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://chulucninh09.visualstudio.com/QuantTrading/_git/batquant",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
