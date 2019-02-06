from setuptools import setup

setup(	name='radnfit',
      	version='0.01',
      	packages=['radnfit'],
	install_requires=[	'numpy>=1.14.2',
				'scipy>=1.0.1',
				'cvxopt>=1.1.9'],
	author='Christian Bongiorno',
	author_email='pvofeta@gmail.com',
	license='GPL',
	zip_safe=False

      )

