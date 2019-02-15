#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='playrobot',
    version='0.0.23',
    description=(
        'lib for playrobot'
    ),
    long_description=open('README.rst').read(),
    author='ckshadow',
    author_email='99robot@playrobot.com',
    maintainer='ckshadow',
    maintainer_email='99robot@playrobot.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='',
	package_data={
        # If any package contains *.txt files, include them:
        '': ['*.*']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'jieba',
        'gTTS',
        'wikipedia',
        'pygame',
        'wave',
        'pyaudio',
        'paho-mqtt',
        'SpeechRecognition',
    ],
)
