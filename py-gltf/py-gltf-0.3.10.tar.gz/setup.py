#!/usr/bin/env python

from distutils.core import setup

from gltf.utils import get_version

setup(
    name='py-gltf',
    version=get_version(),
    author='Trey Nelson',
    packages=['gltf'],
    install_requires=['pyquaternion', 'numpy', 'pillow']
)

