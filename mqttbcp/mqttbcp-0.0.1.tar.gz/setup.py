import setuptools
from distutils.core import setup

setup(
    name='mqttbcp',
    version='0.0.1',
    packages=['mqttbcp'],
    install_requires=['paho-mqtt'],
    url='',
    license='MIT',
    author='athrunen',
    author_email='athrunen@gmail.com',
    description='Basic mqtt command client layered on top of paho mqtt'
)
