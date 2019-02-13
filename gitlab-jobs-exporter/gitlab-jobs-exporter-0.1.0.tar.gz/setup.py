#!/usr/bin/env python
from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    version='0.1.0',
    name='gitlab-jobs-exporter',
    description = "prometheus exporter for exporting job metrics in a project",
    long_description = readme(),
    url = "https://github.com/xinau/gitlab_jobs_exporter",
    author = "Felix Ehrenpfort",
    author_email = "felix.ehrenpfort@protonmail.com",
    packages = find_packages(),
    include_package_data = True,
    scripts=['bin/gitlab_jobs_exporter'],
    license='MIT',
    install_requires=[
        'prometheus-client',
        'python-dateutil'
    ],
    zip_safe=False
)
