from setuptools import setup

setup(
    name='supercommit',
    version='0.1.2',
    author='zhangbinhui',
    packages=['supercommit'],
    install_requires=['Click', 'inquirer', 'terminaltables', 'configparser', 'translate'],
    entry_points='''
        [console_scripts]
        git-sc=supercommit.index:cli
    '''
)