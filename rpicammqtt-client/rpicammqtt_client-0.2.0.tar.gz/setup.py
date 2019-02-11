#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Setup script for rpi-cam-mqtt."""

from setuptools import setup
import io

version = '0.2.0'

setup(
    name="rpicammqtt_client",
    version=version,
    packages=['rpicammqtt_client'],
    install_requires=['PyYaml>=3.12', 'paho-mqtt>=1.4.0'],
    include_package_data=True,

    # metadata
    author="Gianluca Busiello",
    author_email="gianluca.busiello@gmail.com",
    description="Client library to control a raspberry PI camera through MQTT",
    long_description=io.open('README.md', 'r', encoding="UTF-8").read(),
    url="https://gitlab.com/gbus/rpi-cam-mqtt-client",
    package_data={
        'rpicammqtt': ['examples/*.py', 'config/*.yaml'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
    zip_safe=False
)
