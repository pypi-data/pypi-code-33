
import os
from setuptools import setup
from setuptools import find_packages
from pathlib import Path

with open(os.path.join(os.path.dirname(__file__),'version')) as versionfile:
    version = versionfile.read().strip()

long_description = (Path(__file__).parent / 'README.md').read_text()

setup(name='vernum',
    version=version,
    description='Version numbering and git tagging for project releases',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://gitlab.com/francispotter/vernum',
    author='Francis Potter',
    author_email='vernum@fpotter.com',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts':['vernum=vernum.__main__:run']},
    zip_safe=False)
