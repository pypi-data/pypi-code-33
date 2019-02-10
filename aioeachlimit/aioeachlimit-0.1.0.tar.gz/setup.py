from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='aioeachlimit',
    version='0.1.0',
    description='Apply an async function to each item in an array or queue with limited concurrency',
    keywords='asyncio aio each limit concurrency generator synchronization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://github.com/dflupu/aioeachlimit',
    author='Daniel Lupu',
    author_email='dflupu@gmail.com',
    license='MIT',
    packages=['aioeachlimit'],
    zip_safe=False
)
