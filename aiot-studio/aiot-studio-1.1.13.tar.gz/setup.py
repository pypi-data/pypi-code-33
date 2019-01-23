from setuptools import setup

import os
import re
import stat

current_directory = os.path.abspath(os.path.dirname(__file__))

def version():
    with open(os.path.join(current_directory, 'version.meta'), 'r') as v:
        return v.read()

def readme():
    with open(os.path.join(current_directory, 'README.md'), 'r') as v:
        return v.read()

def _readfile(file_name):
    with open(os.path.join(current_directory, file_name), 'r') as v:
        lines = v.readlines()
    return list(filter(lambda x: re.match('^\w+', x), lines))

def requirements():
    return _readfile('requirements.txt')

setup(
    name='aiot-studio',
    version=version(),
    author='mnubo, inc.',
    author_email='support@mnubo.com',
    url='https://smartobjects.mnubo.com/documentation/sdks.html',
    packages=['aiotstudio', 'aiotstudio._core'],
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=requirements(),
    include_package_data=True
)
