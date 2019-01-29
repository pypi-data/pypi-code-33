import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mikuni_pkg",
    version="0.0.7",
    author="Mikuni Motoi",
    author_email="motoimikuni@egmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(),pip 
    install_requires=["numpy", "tensorflow", "mojimoji", "jaconv", "ipython"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6"
    ],
)