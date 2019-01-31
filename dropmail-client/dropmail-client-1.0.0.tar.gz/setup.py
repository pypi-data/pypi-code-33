import setuptools

with open("dropmail/_version.py", "r") as fh:
	exec(fh.read())

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='dropmail-client',
	version=__version__,
	description='A Python interface to https://dropmail.me',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://gitlab.com/JonstonChan/dropmail-client',
	author='Jonston Chan',
	packages=setuptools.find_packages(),
	classifiers=[
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3",
		"Topic :: Communications :: Email"
	],
	install_requires=[
		'websocket-client'
	]
)