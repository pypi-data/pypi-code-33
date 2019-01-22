from os.path import join, dirname
import re

import setuptools


def read_requirements(path):
    requirements = []
    with open(join(dirname(__file__), path), 'r') as handle:
        for line in handle:
            # grab what's before the comment
            line_content = line.split("#")[0].strip()
            if line_content:
                requirements.append(line_content)
    return requirements


def read_file(path):
    with open(path, 'r') as handle:
        return handle.read()

def read_version():
    s = read_file('VERSION')
    m = re.match(r'v(\d+\.\d+\.\d+)', s)
    return m.group(1)

long_description = read_file('README.md')
# install_requires = read_requirements('requirements/install.txt')
# test_requires = read_requirements('requirements/test.txt')
# version = read_version()


setuptools.setup(
    name='miniscule',
    description='A YAML based, pluggable configuration library inspired by Aeson',
    long_description=long_description,
    version='0.2.4',
    url='https://gitlab.com/bartfrenk/miniscule/',
    author='Bart Frenk',
    author_email='bart.frenk@gmail.com',
    package_dir={'miniscule': 'src/miniscule'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    install_requires=['PyYAML>=3'],
    test_requires=['pytest>=4'],
    packages=setuptools.find_packages('src'))
