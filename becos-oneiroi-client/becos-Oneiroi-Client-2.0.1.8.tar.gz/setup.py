import io
from setuptools import setup, find_packages
from os import path





setup(
    name='becos-Oneiroi-Client',
    version='2.0.1.8',
    description='Provides the basic functionality to communincat with Oneiroi 2.0 Daemon',     
    long_description='provides methods to communicate with Oneiroi Daemon and also create node implemenation based on Node Structure',   
    author ='Waqas Ahmed',
    author_email='waqas.ahmed@becos.de',
    license='Apache',
    classifiers=[
                     'Programming Language :: Python :: 3.6',
    ],
    keywords='Oneiroi,becos',
    packages=find_packages(),
    install_requires=['gevent', 'websocket-client', 'sseclient', 'requests','signalr-client','generateDS','lxml']
)