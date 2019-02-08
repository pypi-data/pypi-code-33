from setuptools import setup, find_packages
from os import path

HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'Readme.md')) as f:
    long_description = f.read()

setup(
    name='markdown_notebook',
    keywords='text filter markdown html notebook jupyter',
    description='Python markdown extension to render Jupyter output notation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author= 'Cristian Prieto',
    author_email='me@cprieto.com',
    version='1.0',
    url='http://github.com/cprieto/mdx_notebook',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    packages=find_packages(),
    install_requires = ['Markdown>=2.5']
)
