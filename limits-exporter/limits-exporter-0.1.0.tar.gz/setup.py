#!/usr/bin/env python
from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    version='0.1.0',
    name='limits-exporter',
    description = "prometheus exporter for openstack compute limits in projects",
    long_description = readme(),
    url = "https://github.com/cloudcentric/limits_exporter",
    author = "Felix Ehrenpfort",
    author_email = "felix.ehrenpfort@codecentric.cloud",
    packages = find_packages(),
    include_package_data = True,
    scripts=['bin/limits_exporter'],
    license='MIT',
    install_requires=[
        'openstacksdk',
        'prometheus-client',
    ],
    zip_safe=False
)
