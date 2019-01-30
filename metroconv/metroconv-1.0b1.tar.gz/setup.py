import codecs
import os
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='metroconv',
    version=find_version("metroconv", "__init__.py"),
    packages=find_packages(),
    url='https://github.com/kozmaz87/metroconv',
    license='MIT',
    author='Zoltan Kozma',
    author_email='zoltan@miracode.co.uk',
    description='Metro Bank CSV  to FreeAgent CSV converter',
    entry_points={
        'console_scripts': [
            'metroconv = metroconv.scripts.main:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta'
    ]
)
