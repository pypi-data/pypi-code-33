import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mikuni_pkg",
    version="0.0.4",
    author="Mikuni Motoi",
    author_email="motoimikuni@egmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(),
    install_requires=["numpy", "tensorflow"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6"
    ],
)