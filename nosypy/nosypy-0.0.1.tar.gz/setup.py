from distutils.core import setup
from setuptools import find_packages

with open('README.md') as f:
    readme = f.read()

setup(name='nosypy',
      version='0.0.1',
      description='Novelty and change detection in time lapse',
      url='http://github.com/brett-hosking/nosypy',
      license='MIT',
      author='brett hosking',
      author_email='wilski@noc.ac.uk',
      packages=find_packages())
