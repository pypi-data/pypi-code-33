import os
from setuptools import setup


def read(*fname):
    with open(os.path.join(os.path.dirname(__file__), *fname)) as f:
        return f.read()


try:
    version = read('VERSION').strip()
except FileNotFoundError:
    version = '0'


setup(
    name='dicetrust',
    description='DiceTrust API Client',
    version=version,
    author=u'Cenk Altı',
    author_email='cenkalti@gmail.com',
    url='https://github.com/dicetrust/dicetrust.py',
    py_modules=['dicetrust'],
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'requests',
        'sseclient',
    ],
    entry_points={
        'console_scripts': [
            'dicetrust = dicetrust:_entry_point',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
