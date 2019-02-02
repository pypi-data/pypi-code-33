import os

from setuptools import setup

def get_long_desctiption():
    readme_file = open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r')
    return readme_file.read()


setup(
    name='icelander_generator',
    packages=['icelander_generator'], # this must be the same as the name above
    version='0.1.1',
    description='A utility to generate random Icelanders',
    author='7oi',
    author_email='7oi@7oi.is',
    long_description=get_long_desctiption(),
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/7oi/IcelanderGenerator',
    install_requires=[
        'lxml==4.3.0',
        'requests==2.21.0',
        'kennitala==0.1.3'
    ],
    include_package_data=True,
    keywords=['tests', 'generator'],
    classifiers = [],
)
