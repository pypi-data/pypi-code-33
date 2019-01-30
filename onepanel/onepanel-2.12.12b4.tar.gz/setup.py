from setuptools import setup

from onepanel.constants import *

setup(
    name="onepanel",
    version=CLI_VERSION,
    packages = ['onepanel', 'onepanel.commands','onepanel.utilities','onepanel.git_hooks'],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=[
        'prettytable',
        'requests',
        'click>=7',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize',
        'configparser',
        'awscli'
    ],
    setup_requires=[
        'prettytable',
        'requests',
        'click>=7',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize',
        'configparser',
        'awscli'],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:main
    ''',
)
