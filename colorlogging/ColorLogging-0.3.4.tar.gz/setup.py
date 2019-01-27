from setuptools import setup

setup(
    name='ColorLogging',
    version='0.3.4',
    description='A simple Python logger with colored log levels',
    url='http://github.com/tjkessler/ColorLogging',
    author='Travis Kessler',
    author_email='travis.j.kessler@gmail.com',
    license='MIT',
    packages=['colorlogging'],
    install_requires=['colorama'],
    zip_safe=False
)
