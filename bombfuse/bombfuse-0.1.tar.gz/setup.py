import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="bombfuse",
    version="0.1",
    author="The Munshi Group",
    author_email="support@munshigroup.com",
    description="Specify a timeout with any given function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/munshigroup/bombfuse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)