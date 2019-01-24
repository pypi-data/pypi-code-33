#!/usr/bin/env python3

from setuptools import setup


setup(
    name='helm-template-generator',
    version='1.0',
    description='Generate helm template files for aether',
    url='http://github.com/ehealthafrica/ehealh-deployment',
    author='Oluwafemi Olofintuyi',
    author_email='devops@ehealthafrica.org',
    license='MIT',
    install_requires=['mako'],
    packages=['helm_template_generator'],
    package_data={
        'helm_template_generator': [
            'templates/*.tmpl.yaml',
            'templates/*.tmpl.txt',
            'templates/*.tmpl.tpl']},
    entry_points={
                'console_scripts': ['helm-template-generator=helm_template_generator.generator:main'],
                },
    zip_safe=False)
