from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.0.2'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs

all_reqs = [
    'colorlog==4.0.2'
]
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='ez-logger',
    version=__version__,
    description='ez-logger allows you to create commonly used logger for everyday operations.',
    long_description=long_description,
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 2.7',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*', '.idea']),
    include_package_data=True,
    author='Rakesh V',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='varma.rakesh@gmail.com',
    url='https://github.com/varmarakesh/ez-logger'
)
