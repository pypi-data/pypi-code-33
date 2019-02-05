from setuptools import setup

setup(
	name = 'hdir',
	version = '0.2',
	description = 'Highlight dir',
	url = 'http://phyl.io/?page=hdir.html',
	author = 'Philippe Kappel',
	author_email = 'philippe.kappel@gmail.com',
	license = 'MIT',
	long_description = "`hdir` is a highlighted version of the `dir` function.",
	long_description_content_type = 'text/markdown',
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Topic :: Software Development',
		'Topic :: Utilities'],
	packages = ['hdir'],
	install_requires = ['ansiwrap']
)