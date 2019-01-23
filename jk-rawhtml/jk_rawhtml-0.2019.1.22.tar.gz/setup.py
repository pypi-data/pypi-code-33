from setuptools import setup


def readme():
	with open("README.rst") as f:
		return f.read()


setup(name="jk_rawhtml",
	version="0.2019.1.22",
	description="This python module provides support for programmatically generating HTML5 code.",
	author="Jürgen Knauth",
	author_email="pubsrc@binary-overflow.de",
	license="Apache 2.0",
	url="https://github.com/jkpubsrc/python-module-jk-rawhtml",
	download_url="https://github.com/jkpubsrc/python-module-jk-rawhtml/tarball/0.2019.1.22",
	keywords=[
		"html",
		"css",
		"html5",
		],
	packages=[
		"jk_rawhtml",
		],
	install_requires=[
	],
	include_package_data=True,
	classifiers=[
		"Development Status :: 4 - Beta",
		#"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: Apache Software License",
	],
	long_description=readme(),
	zip_safe=False)

