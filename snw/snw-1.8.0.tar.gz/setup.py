from setuptools import setup

setup(
    name='snw',
    version='1.8.0',
    description='snw client tool',
    author='Jean Senellart',
    author_email='jean.senellart@systrangroup.com',
    url='http://www.systransoft.com',
    scripts=['client/snw'],
    package_dir={'': 'nmt-wizard'},
    packages=['client'],
    install_requires=[
        'prettytable',
        'regex',
        'requests',
        'six',
        'setuptools',
        'jsonschema',
        'packaging>=17.0'
    ]
)
