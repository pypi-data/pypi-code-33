import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ryakugo_pkg",
    version="0.0.2",
    author="Mikuni Motoi",
    author_email="mtotoimikuni@egmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(),pip 
    install_requires=["numpy", "mojimoji", "jaconv", "ipython", "keras", "pykakasi"],
    dependency_links = ["https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.10.0-py3-none-any.whl"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6"
    ],
)
# numpy==1.15.4
# tensorflow==1.12.0
# Keras==2.2.4
# jaconv==0.2.3
# import pickle -> ipython
# mojimoji==0.0.8
# pykakasi