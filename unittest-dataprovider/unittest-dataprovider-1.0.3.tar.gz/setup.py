import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='unittest-dataprovider',
    version='1.0.3',
    description='PHPUnit-like @dataprovider decorator for unittest',
    author='drm from melp.nl, packaged for reuse by James Pic',
    author_email='jamespic@gmail.com',
    url='http://github.com/l-vo/unittest-data-provider',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.rst'),
    license='MIT',
    keywords='unittest dataprovider',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
