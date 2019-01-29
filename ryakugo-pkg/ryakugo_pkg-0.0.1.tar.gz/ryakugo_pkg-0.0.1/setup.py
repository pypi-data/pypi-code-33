import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ryakugo_pkg",
    version="0.0.1",
    author="Mikuni Motoi",
    author_email="mtotoimikuni@egmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(),pip 
    install_requires=["numpy", "tensorflow", "mojimoji", "jaconv", "ipython", "keras", "pykakasi"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6"
    ],
)