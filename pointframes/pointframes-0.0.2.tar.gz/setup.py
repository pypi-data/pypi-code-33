from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='pointframes',
    version='0.0.2',
    url='https://github.com/3Dimaging-ucl/pointframes',
    description='PointFrames - A Scalable Point Code Library',
    author='David Griffiths',
    author_email='david.griffiths.16@ucl.ac.uk',
    packages=find_packages(),
    install_requires=['open3d-python',
                      'numpy',
                      'pandas',
                      'pyarrow',
                      'tables',
                      'scikit-learn']
)
