from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='NanostructureUCPH',
      version='0.0.1',
      description='Pakage for analyzing nanostructures',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
 	    'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Chemistry'
      	],
      keywords='structure science',
      url='https://github.com/EmilSkaaning/NanostructureUCPH',
      author='Emil Thyge Skaaning Kjaer',
      author_email='rsz113@alumni.ku.dk',
      license='MIT',
      packages=[
      	'NanostructureUCPH', 
      	'NanostructureUCPH/CifConverter'
      	],
      install_requires=[
        'numpy',
      	],
      include_package_data=True,
      zip_safe=False)
