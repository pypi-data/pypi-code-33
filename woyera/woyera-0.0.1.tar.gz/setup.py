import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="woyera",
    version="0.0.1",
    author="Woyera Team",
    author_email="admin@woyera.com",
    description="Library for Woyera API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asharma327/woyera_python.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)