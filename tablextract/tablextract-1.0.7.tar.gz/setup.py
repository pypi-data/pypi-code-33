from setuptools import find_packages, setup

with open('README.md', 'r') as fh:
	long_description = fh.read()

setup(
	name='tablextract',
	version='1.0.7',
	author='Juan C. Roldan',
	author_email='juancarlos@sevilla.es',
	description='Extract the information represented in any HTML table',
	long_description=long_description,
	long_description_content_type='text/markdown',
	install_requires=[
		'bs4>=4.6.3',
		'etk>=2.1.6',
		'nltk>=3.3',
		'requests>=2.18.4',
		'scikit-learn>=0.20.0',
		'wikipedia-api>=0.3.7',
		'selenium>=3.14.1'
	],
	url='https://github.com/juancroldan/tablextract',
	packages=find_packages(),
	package_data={'': ['resources/add_render.js']},
	include_package_data=True,
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
)