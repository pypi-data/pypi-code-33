'''Query the IP address of the external network.'''

import os.path

from setuptools import setup


# What packages are required for this module to be executed?
requires = [
    'requests',
]

# Import the README and use it as the long-description.
cwd = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(cwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='external-ip',
    py_modules=['external_ip'],
    version='0.1.0',
    license='BSD',
    author='White Turing',
    author_email='fujiawei@stu.hznu.edu.cn',
    description='Query the IP address of the external network.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fjwCode/external-ip',
    keywords=['ip', 'tool', 'internet'],
    entry_points={
        'console_scripts': [
            'ip = external_ip:external_ip',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=requires,
)
