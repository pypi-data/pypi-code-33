import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name="movies_module_micah",
    version="1.3.0",
    author="Vincent",
    author_email="micahkabala@outlook.com",
    description="Micah-specific exercise modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/micang404/movies_module_micah",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)