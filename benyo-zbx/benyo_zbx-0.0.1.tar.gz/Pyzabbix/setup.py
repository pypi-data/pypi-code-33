try:
	from setuptools import setup
except:
	from distutils.core import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Pyzabbix',
    version='0.0.1',
    description='zabbix api for pypi',
    long_description=long_description,
    url='http://pythonhosted.org/Pyzabbix/',
    author='Benyo Yuan',
    author_email='yuyuhupo@outlook.com',
    license='MIT',
    platforms=['linux/Windows'],
    keywords='zabbix monitor',
    packages=['Pyzabbix'],
    install_requires=['request'],
    tests_require=['nose', 'coverage', 'jsonschema'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)