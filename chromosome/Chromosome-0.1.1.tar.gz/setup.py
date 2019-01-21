#!

from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='Chromosome',
      version='0.1.1',
      description='Evolutionary Algorithm Framework in Python',
      author='Trey Guest',
      author_email='twguest@students.latrobe.edu.au',
      url='https://www.github.com/twguest/Chromosome',
      packages=find_packages(exclude=['examples']),
      platforms=['any'],
      keywords=['evolutionary algorithms','genetic algorithms','genetic programming','cma-es','ga','gp','es','pso', 'artificial intelligence', 'ai'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='LGPL',
      classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        ],
     use_2to3=True
)
