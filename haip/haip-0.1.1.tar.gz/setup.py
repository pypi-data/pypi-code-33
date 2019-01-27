import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="haip",
    version="0.1.1",
    author="Reinhard Hainz",
    author_email="reinhard.hainz@gmail.com",
    description="The root element of the haip namespace.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haipdev/haip",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
