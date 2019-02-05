import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lforchiniHTTP",
    version="0.1.1",
    author="LForchini",
    author_email="leonardo.forchini@gmail.com",
    description="A simple HTTP server with a custom handler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lforchini/HTTP-Server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
