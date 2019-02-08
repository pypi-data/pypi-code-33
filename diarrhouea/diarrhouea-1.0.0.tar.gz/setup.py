#!/usr/bin/env python3

import setuptools, diarrhouea

setuptools.setup(
	name="diarrhouea",
	version=diarrhouea.__version__,
	
	py_modules=[
		"diarrhouea"
	],
	
	include_package_data=True,
	
	entry_points={
		"console_scripts": [
			"diarrhouea = diarrhouea:main"
		]
	},
	
	author="Kirby Kevinson (0x46d59b71)",
	author_email="0x46d59b71@protonmail.com",
	
	license="BSD Zero Clause License",
	
	description=diarrhouea.__description__,
	
	long_description=open("README.md", "r").read(),
	long_description_content_type="text/markdown",
	
	keywords="terminal emulator",
	
	url="https://gitlab.com/0x46d59b71/diarrhouea",
	
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: X11 Applications :: GTK",
		"License :: OSI Approved",
		"Operating System :: POSIX",
		"Programming Language :: Python :: 3",
		"Topic :: Terminals :: Terminal Emulators/X Terminals"
	]
)
