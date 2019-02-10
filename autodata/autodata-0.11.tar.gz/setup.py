from setuptools import setup
import os

long_description = "Auto allocation dict and list"
if os.path.exists("readme.md"):
    with open("readme.md") as f:
        long_description = f.read()

setup(
    name = 'autodata',
    version = '0.11',
    url = 'https://github.com/shii4c/PythonAutoData',
    author = 'Kenichiro SHII',
    author_email = 'shii4c@gmail.com',
    license = 'MIT',
    description = 'Auto allocation dict and list',
    long_description = long_description,
    classifiers = [
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License'
    ],
    zip_safe = False,
    packages = ['autodata']
)
