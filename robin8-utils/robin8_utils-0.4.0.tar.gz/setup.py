import setuptools


def get_description():
    with open('README.md', 'r') as f:
        long_description = f.read()

    return long_description


def get_version():
    with open('VERSION', 'r') as f:
        version = f.read().strip()

    return version


setuptools.setup(
    name='robin8_utils',
    version=get_version(),
    author='Robin8',
    author_email='vvasyuk@robin8.com',
    description='Utils used in Robin8 projects',
    long_description=get_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/Robin8Put/pmes/tree/master/utils',
    packages=setuptools.find_packages(),
    install_requires=(
        'apply-defaults',
        'attrdict',
        'base58check',
        'bip32utils',
        'certifi',
        'chardet',
        'cytoolz',
        'ecdsa',
        'eth-abi',
        'eth-account',
        'eth-hash',
        'eth-keyfile',
        'eth-keys',
        'eth-rlp',
        'eth-typing',
        'eth-utils',
        'funcsigs',
        'hexbytes',
        'idna',
        'jsonrpcclient<=2.6.0',
        'jsonrpcserver',
        'jsonschema',
        'lru-dict',
        'motor',
        'parsimonious',
        'pycryptodome',
        'pymongo',
        'requests',
        'rlp',
        'pysha3',
        'six',
        'toolz',
        'tornado',
        'urllib3',
        'web3'
    ),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ),
)