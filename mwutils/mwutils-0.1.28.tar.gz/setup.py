from setuptools import setup, find_packages
from codecs import open
import os

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f),encoding='utf8').read().strip()

setup(
    name='mwutils',
    version='0.1.28',
    description='maxwin团队常用的utils ',
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/maxwin-inc/mwutils/src',  # Optional
    author='cxhjet',  # Optional
    author_email='cxhjet@qq.com',  # Optional
    packages=find_packages(),  # Required
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['redis==2.10.6','python-consul>=1.1.0',
                      'ciso8601>=2.1.1']
)
