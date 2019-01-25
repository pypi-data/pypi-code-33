import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="paynspray",
    version="0.1.5",
    author="The Munshi Group",
    author_email="support@munshigroup.com",
    description="Provides access to functions pertaining to text generation, manipulation, & presentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/munshigroup/paynspray",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)