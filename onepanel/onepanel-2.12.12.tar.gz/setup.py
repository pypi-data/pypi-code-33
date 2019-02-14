from setuptools import setup

from onepanel.constants import *

setup(
    name="onepanel",
    version=CLI_VERSION,
    packages=['onepanel', 'onepanel.commands', 'onepanel.types', 'onepanel.models',
              'onepanel.utilities', 'onepanel.utilities.s3', 'onepanel.git_hooks'],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        'configparser',
        'PyYAML<=3.13,>=3.10',
        'prettytable',
        'requests',
        'click>=7',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize',
        'awscli==1.16.103',
        'boto3>=1.9.89',
        'watchdog',
        'iso8601',
        'future'
    ],
    setup_requires=[
        'configparser',
        'PyYAML<=3.13,>=3.10',
        'prettytable',
        'requests',
        'click>=7',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize',
        'watchdog',
        'iso8601',
        'future'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:main
    ''',
)
