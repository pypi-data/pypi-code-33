from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
	name="speckle", 
	description="Python client for Speckle framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",	
	url="https://github.com/speckleworks/",
	author="Tom Svilans",
	author_email="tom.svilans@gmail.com",
	license="MIT",
	version="0.2.7",
	packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],	
	)