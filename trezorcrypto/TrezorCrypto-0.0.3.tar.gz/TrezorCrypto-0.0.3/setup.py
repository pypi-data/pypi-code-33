#!/usr/bin/env python3

from setuptools import setup, Extension
from Cython.Build import cythonize


TREZOR_CRYPTO_SOURCES = [
    'aes/aescrypt.c',
    'aes/aeskey.c',
    'aes/aes_modes.c',
    'aes/aestab.c',
    'aes/aestst.c',
    'address.c',
    'base58.c',
    'bip32.c',
    'bip39.c',
    'bignum.c',
    'blake256.c',
    'blake2b.c',
    'blake2s.c',
    'curves.c',
    'ecdsa.c',
    'ed25519-donna/curve25519-donna-32bit.c',
    'ed25519-donna/ed25519.c',
    'ed25519-donna/ed25519-donna-impl-base.c',
    'ed25519-donna/ed25519-donna-basepoint-table.c',
    'ed25519-donna/ed25519-donna-32bit-tables.c',
    'ed25519-donna/ed25519-keccak.c',
    'ed25519-donna/ed25519-sha3.c',
    'ed25519-donna/curve25519-donna-helpers.c',
    'ed25519-donna/curve25519-donna-scalarmult-base.c',
    'ed25519-donna/modm-donna-32bit.c',
    'groestl.c',
    'hasher.c',
    'hmac.c',
    'memzero.c',
    'nist256p1.c',
    'pbkdf2.c',
    'rand.c',
    'ripemd160.c',
    'secp256k1.c',
    'sha2.c',
    'sha3.c',
]

ext_modules = [
    Extension('trezorcrypto',
        sources=[
            'extmod/trezorcrypto/trezorcrypto.pyx',
        ] + TREZOR_CRYPTO_SOURCES,
        include_dirs=[
            '.',
            'aes',
        ]
    ),
]


description='Cython wrapper around trezor-crypto library'

long_description=('Cython bindings for '
                  'https://github.com/trezor/trezor-crypto. '
                  'Use for reference / educational purposes only.')


setup(
    name='TrezorCrypto',
    version='0.0.3',
    license='MIT',
    url='https://github.com/trezor/trezor-crypto',
    ext_modules=cythonize(ext_modules),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3 :: Only',
    ],
    description=description,
    long_description=long_description,
)
