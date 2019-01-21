from setuptools import find_namespace_packages, setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="aliceplex-scrap",
    version="2.0.1",
    author="Alice Plex",
    url="https://gitlab.com/alice-plex/scrap",
    description="Scraper library for Plex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=find_namespace_packages(include=["aliceplex.*"]),
    install_requires=[
        "aliceplex-serialize>=2.0.0,<3.0.0",
        "aliceplex-schema>=3.0.2,<4.0.0",
        "requests>=2.21.0,<3.0.0",
        "beautifulsoup4>=4.7.1,<5.0.0",
        "selenium>=3.141.0,<4.0.0",
        "html5lib>=1.0.1,<2.0.0",
        "Pillow>=5.4.1,<6.0.0"
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    )
)
