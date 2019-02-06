from setuptools import setup

setup(
    name='e4client',
    version='1.12',
    packages=['e4client'],
    author='khvilaboa',
    description='Client to download information of the E4 Connect platform.',
    install_requires=[
        'requests',
    ],
    scripts=['e4client/e4client']
)
