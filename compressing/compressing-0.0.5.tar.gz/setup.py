import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="compressing",
    version="0.0.5",
    author="Flavio Barros",
    author_email="juniorbarros3@gmail.com",
    description="Compressao de provas",
    long_description="Compressao de provas...",
    long_description_content_type="text/markdown",
    url="http://github.com/flavio-barros/compressing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
)
