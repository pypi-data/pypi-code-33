from setuptools import setup, find_packages
from codecs import open
from os import path


VERSION = 'v0.0.2'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Docify',
    version=VERSION,
    description='Simple, flexible python document generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rapidstack/docify',
    download_url='https://github.com/rapidstack/docify/archive/%s.tar.gz' % VERSION,
    author='Arijit Basu',
    author_email='sayanarijit@gmail.com',
    license='MIT',
    py_modules=['docify'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft'
    ],
    platforms=['Any'],
    keywords='documents generator writer',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=[]
)
