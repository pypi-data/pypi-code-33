from setuptools import setup
from supercommit import Version

setup(
    name='supercommit',
    version=Version,
    author='zhangbinhui',
    author_email="maru-zhang@foxmail.com",
    packages=['supercommit'],
    install_requires=['Click', 'inquirer', 'terminaltables', 'configparser', 'translate'],
    entry_points='''
        [console_scripts]
        git-sc=supercommit.index:cli
    '''
)