from setuptools import setup


def readme():
	with open('README.rst') as f:
		return f.read()


setup(name='jk_logging',
	version='0.2018.12.28',
	description='This is a logging framework.',
	author='Jürgen Knauth',
	author_email='pubsrc@binary-overflow.de',
	license='Apache 2.0',
	url='https://github.com/jkpubsrc/python-module-jk-logging',
	download_url='https://github.com/jkpubsrc/python-module-jk-logging/tarball/0.2018.12.28',
	keywords=[
		'debugging',
		'logging'
		],
	packages=[
		'jk_logging'
		],
	install_requires=[
	],
	include_package_data=True,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Programming Language :: Python :: 3.5',
		'License :: OSI Approved :: Apache Software License'
	],
	long_description=readme(),
	zip_safe=False)

