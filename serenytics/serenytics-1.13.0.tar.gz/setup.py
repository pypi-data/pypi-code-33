import sys
import os.path as osp
from setuptools import setup, find_packages


__version__ = None
path_version = osp.join(osp.dirname(__file__), 'serenytics/version.py')
if sys.version_info[0] == 3:
    exec(open(path_version).read())
else:
    execfile(path_version)  # noqa


setup(
    name='serenytics',
    version=__version__,
    description='Serenytics API client for python',
    install_requires=['requests[security] >= 2.8.1', 'pandas >= 0.16', 'paramiko >= 1.16'],
    packages=find_packages(),
    include_package_data=True,
    author='Serenytics Team',
    author_email='support@serenytics.com',
    url='https://www.serenytics.com',
    keywords=['serenytics', 'backend', 'hosted', 'cloud',
              'bi', 'dashboard', 'scripts', 'etl'],
    classifiers=[
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
