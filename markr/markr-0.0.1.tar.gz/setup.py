import os
from setuptools import setup

# Taken from https://github.com/kennethreitz/setup.py/blob/master/setup.py
here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='markr',
    version='0.0.1',
    description='Package and script allowing marks to be associated with files',
    url='https://github.com/dang3r/markr',
    author='Daniel Cardoza',
    author_email='dan@danielcardoaa.com',
    license='MIT',
    packages=['markr'],
    python_requires='>=3.4.0',
    scripts=['bin/markr'],
    install_requires=['pyxattr'],
    long_description='\n' + open(os.path.join(here, 'README.md')).read(),
    long_description_content_type='text/markdown',
    zip_safe=False
)
