import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="yomari",
    version="0.0.1",
    description="Yet Another Language Toolkit",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/awalesushil/yomari",
    author="Sushil Awale",
    author_email="ssushil.awale@gmail.com",
    license="MIT",
    keywords="language toolkit, nlp, nepali language, newari language",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages= find_packages(),
)