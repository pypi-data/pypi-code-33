#!/usr/bin/env python
import os
from setuptools import setup


setup(
    name='dkUtil',
    version='0.1.10',
    description="Python dianke sms util function",
    author='MICHAEL.xu',
    author_email='xumanhua@feibank.com',
    py_modules=['otsapi','mqapi','sqlapi','decipheringapi','functionapi'],
    package_dir={'': 'src'},
    license='No LICENSE',
    zip_safe=False,
    url='http://git.taiyear.cn/michael/util.git',
    # include_package_data=True,
    setup_requires=['configparser','pika','tablestore','mysqlclient'],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)