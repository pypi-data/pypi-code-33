
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="idebug",
    version="0.0.3",
    author="innovata sambong",
    author_email="iinnovata@gmail.com",
    description="innovata-debug",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/innovata/ilib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
