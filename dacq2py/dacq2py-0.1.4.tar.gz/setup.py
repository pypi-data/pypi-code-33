from setuptools import setup

setup(name='dacq2py',
	  version='0.1.4',
	  description='Analysis of electrophysiological data recorded with the Axona recording system',
	  url='https://github.com/rhayman/dacq2py',
	  author='Robin Hayman',
	  author_email='r.hayman@ucl.ac.uk',
	  license='MIT',
	  packages=['dacq2py'],
	  install_requires=[
	  	'numpy',
	  	'scipy',
	  	'matplotlib',
	  	'astropy',
	  	'scikit-image',
	  	'mahotas',
	  	'scikits.bootstrap'
	  ],
	  zip_safe=False)
