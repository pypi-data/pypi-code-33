import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ccpl",
    version="0.1.2",
    author="Rainbow Doge",
    author_email="realrainbowdoge@gmail.com",
    description="ColorfulCore Python Library - CCPL for short.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.rainbowdoge.000webhostapp.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)