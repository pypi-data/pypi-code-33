import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
   name='bigmpi4py',
   version='1.2.3',
   description='BigMPI4py: Python module for parallelization of Big Data objects',
   long_description=long_description,
   license="LICENSE",
   author='Alex M. Ascension',
   author_email='alexmascension@gmail.com',
   url="https://gitlab.com/alexmascension/bigmpi4py",
   install_requires=['mpi4py>=3.0.0','numpy>=1.14.3', 'pandas>=0.23.4', 'psutil>=5.4.5', 'jupyter>=1.0.0', 'matplotlib>=2.2.3', 'seaborn>=0.8.1'], #external packages as dependencies
   packages=setuptools.find_packages(),
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
      "Operating System :: OS Independent",
   ],
) 
