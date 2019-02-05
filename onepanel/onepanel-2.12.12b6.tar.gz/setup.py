from setuptools import setup

from onepanel.constants import *

setup(
    name="onepanel",
    version=CLI_VERSION,
    packages=['onepanel', 'onepanel.commands', 'onepanel.types', 'onepanel.models',
              'onepanel.utilities', 'onepanel.utilities.s3', 'onepanel.git_hooks'],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        'PyYAML==3.13',
        'prettytable',
        'requests',
        'click',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize',
        'configparser',
        'boto3==1.9.62',
        'awscli',
        'watchdog==0.9.0',
        'iso8601',
        'future'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:main
    ''',
)
