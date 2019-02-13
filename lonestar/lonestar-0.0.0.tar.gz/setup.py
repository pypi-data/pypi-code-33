import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lonestar",
    version="0.0.0",
    author="Jim Kitchen",
    author_email="jim22k@gmail.com",
    description="Delayed execution DSL operating on tabular data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
