# Always prefer setuptools over distutils
import setuptools
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='pydeid',
    version='0.0.1',
    description='Annotate and remove personal identifiers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/MIT-LCP/pydeid',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[]
    )