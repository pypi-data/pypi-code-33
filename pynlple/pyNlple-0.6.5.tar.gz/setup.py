from setuptools import setup, find_packages
from pynlple import __version__

setup(
    name='pyNlple',
    packages=find_packages(exclude=['scripts']),
    include_package_data=True,
    version=__version__,
    description='NLP procedures in python brought to you by YouScan.',
    author='Paul Khudan',
    author_email='pk@youscan.io',
    company='YouScan Limited',
    url='https://github.com/YouScan/pyNlple',
    install_requires=['ipython',
                      'numpy',
                      'scikit-learn',
                      'requests>=2.9.1',
                      'pandas>=0.19.0',
                      'gensim>=2.1.0',
                      'elasticsearch>=2.0.0,<3.0.0',
                      'pymorphy2',
                      'emoji'],

    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='pynlple.tests',

)