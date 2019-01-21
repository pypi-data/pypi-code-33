# -*- coding: utf-8 -*-
from setuptools import setup

from performance import VERSION

setup(
    name='gitcepter',
    version='.'.join(str(v) for v in VERSION),
    url='http://appinstall.aiyoumi.com:8282/qinchao/ptk.git',
    packages=['performance'],
    author='chao',
    author_email='qinchao@aicaigroup.com',
    platforms='POSIX',
    description='android performance test kit',
    long_description="",
    keywords=(
        'android, memory, performance, auto testing'
    ),
    entry_points={
        'console_scripts': [
            'ptk=performance.ptk:main',
        ],
    },
)