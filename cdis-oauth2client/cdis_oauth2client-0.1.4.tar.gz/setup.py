from setuptools import setup


setup(
    name='cdis_oauth2client',
    version='0.1.4',
    description='Flask blueprint and utilities for oauth2 client',
    url='https://github.com/uc-cdis/cdis_oauth2client',
    license='Apache',
    packages=[
        'cdis_oauth2client',
    ],
    install_requires=[
        'Flask',
        'requests>=2.5.2,<3.0.0',
        'cdispyutils>=0.2.11',
    ],
)
