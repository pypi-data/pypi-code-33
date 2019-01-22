import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="synk",
	version="0.0.1",
	author="Jimmy Dias",
	author_email="jimmy@synksuite.com",
	description="synk command line interface and related libraries",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/synksuite/synk-cli",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)