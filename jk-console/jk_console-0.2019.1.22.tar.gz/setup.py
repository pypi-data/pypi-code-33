from setuptools import setup


def readme():
	with open("README.rst") as f:
		return f.read()


setup(name="jk_console",
	version="0.2019.1.22",
	description="This python module provides a variety of essential functionality for implementing versatile programs using the console. (Please have a look at the documentation for details.)",
	author="Jürgen Knauth",
	author_email="pubsrc@binary-overflow.de",
	license="Apache 2.0",
	url="https://github.com/jkpubsrc/python-module-jk-console",
	download_url="https://github.com/jkpubsrc/python-module-jk-json/tarball/0.2019.1.22",
	keywords=[
		"console",
		"terminal",
		"colors",
		"stdin"
		],
	packages=[
		"jk_console"
		],
	install_requires=[
	],
	include_package_data=True,
	classifiers=[
		"Development Status :: 4 - Beta",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: Apache Software License"
	],
	long_description=readme(),
	zip_safe=False)

