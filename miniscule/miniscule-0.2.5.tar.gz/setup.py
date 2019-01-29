import re

import setuptools

def read_file(path):
    with open(path, 'r') as handle:
        return handle.read()

def read_version():
    try:
        s = read_file('VERSION')
        m = re.match(r'v(\d+\.\d+\.\d+)', s)
        return m.group(1)
    except FileNotFoundError:
        return "0.0.0"

long_description = read_file('README.md')
version = read_version()


setuptools.setup(
    name='miniscule',
    description='A YAML based, pluggable configuration library inspired by Aeson',
    long_description=long_description,
    include_package_data=True,
    version=version,
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
    install_requires=["PyYAML>=3"],
    data_files=[('.', ['VERSION'])],
    setup_requires=['pytest-runner'],
    tests_require=["pytest>=4"],
    packages=setuptools.find_packages('src'))
