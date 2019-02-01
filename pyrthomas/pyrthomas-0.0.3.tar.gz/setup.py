import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrthomas",
    version="0.0.3",
    author="Talha Junaid",
    author_email="talhajunaidd@gmail.com",
    description="Python implementation for Rene` Thomas's Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['networkx==2.2']
)
