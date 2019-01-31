import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="bashify",
	version="0.1.1",
	author="David Kamer",
	author_email="me@davidkamer.com",
	description="A package to print and execture bash files",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/UniWrighte/bashify",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	],
)