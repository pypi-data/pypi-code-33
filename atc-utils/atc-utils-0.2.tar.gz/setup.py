try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='atc-utils',
    version='0.2',
    platforms=['all'],
    url='http://www.zhangyue.com',
    license='MIT',
    author='autotest',
    author_email='autotest.list@zhangyue.com',
    description='',
    keywords=('testing', 'atc', 'util'),
    packages=['atc_utils','atc_utils.core'],
    zip_safe=False
)
