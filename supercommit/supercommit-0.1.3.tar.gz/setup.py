from setuptools import setup

setup(
    name='supercommit',
    version='0.1.3',
    author='zhangbinhui',
    author_email="maru-zhang@foxmail.com",
    packages=['supercommit'],
    data_files=[('supercommit', ['supercommit/commit-msg', 'supercommit/swiftlint-clip.sh', 'supercommit/swiftlint-lint.sh', 'supercommit/swiftlint-rule.yml'])],
    install_requires=['Click', 'inquirer', 'terminaltables', 'configparser', 'translate'],
    entry_points='''
        [console_scripts]
        git-sc=supercommit.index:cli
    '''
)