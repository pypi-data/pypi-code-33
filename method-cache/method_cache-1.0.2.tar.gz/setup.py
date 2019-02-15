import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="method_cache",
    version="1.0.2",
    author="Stefan Eiermann",
    author_email="python-org@ultraapp.de",
    description="Simple TTL Cache for methods and there results.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eieste/MethodCache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)


