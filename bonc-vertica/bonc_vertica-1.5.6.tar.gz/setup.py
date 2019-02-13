
from setuptools import setup

import bonc_vertica

setup(
    name='bonc_vertica',
    version=bonc_vertica.__version__,
    author=bonc_vertica.__author__,
    author_email=bonc_vertica.__mail__,
    description=bonc_vertica.__description__,
    packages=['bonc_vertica'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bonc-vertica=bonc_vertica.main: main',
        ]
    },
    install_requires=[
        'vertica-python>=0.8.0',
        'sqlparse>=0.2.4',
        # 'ibm-db>=2.0.9',
        'zoran_tools>=0.1.20',
    ],
)