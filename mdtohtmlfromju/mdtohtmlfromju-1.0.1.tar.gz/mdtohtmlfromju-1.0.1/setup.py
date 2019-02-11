import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdtohtmlfromju",
    version="1.0.1",
    author="Julien Castera",
    author_email="onair921@gmail.com",
    description="A small package which convert markdown to HTML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JulienCASTERA/MDtoHTML",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)