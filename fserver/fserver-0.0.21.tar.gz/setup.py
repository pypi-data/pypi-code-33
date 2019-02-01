# -*- coding: utf-8 -*-
import sys
import time

from setuptools import setup

from fserver import conf

now = time.strftime('%Y/%m/%d', time.localtime(time.time()))
if conf.BUILD_TIME != now:
    print('conf.BUILD_TIME is invalid: %s != %s' % (conf.BUILD_TIME, now))
    sys.exit(-1)
if conf.DEBUG:
    print('debug mode is open by default')
    sys.exit(-1)

setup(
    name='fserver',
    version=conf.VERSION,
    description='a simple http.server implement by flask',
    url='https://github.com/Carrotor116/fserver',
    author='Nonu',
    author_email='1162365377@qq.com',
    license='MIT',
    packages=['fserver'],
    install_requires=['Flask >= 1.0.2', 'gevent >= 1.3.6'],
    package_data={
        '': ['templates/*.html', 'static/*']
    },
    entry_points={
        'console_scripts': [
            'fserver=fserver:command_line.run_fserver'
        ]
    }
)

# python setup.py sdist bdist_wheel --universal
# twine upload dist/*
