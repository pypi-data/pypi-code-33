import setuptools

with open("README.md","r") as fh:
    long_description=fh.read()

setuptools.setup(
    name        = 'py-file',
    version     = '1.2.0',
    py_modules  = ['py_file'],
    author      = 'wunan',
    author_email= '631779874@qq.com',
    url         = 'http://www.headfirstlabs.com',
    description = 'A simple printer of nested lists',
    classifiers = ["Programming Language :: Python :: 3",],
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = setuptools.find_packages(),
    )
