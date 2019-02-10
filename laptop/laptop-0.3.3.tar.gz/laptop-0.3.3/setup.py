
import os
from setuptools import setup
from setuptools import find_packages
from pathlib import Path

with open(os.path.join(os.path.dirname(__file__),'version')) as versionfile:
    version = versionfile.read().strip()

bindir = os.path.join(os.path.dirname(__file__),'bin')

long_description = (Path(__file__).parent / 'README.md').read_text()

setup(name='laptop',
    version=version,
    description='Command-line tools for the HP Spectre laptop and Fujitsu ScanSnap scanner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/fpotter/tools/laptop',
    author='Francis Potter',
    author_email='laptop@fpotter.com',
    license='MIT',
    packages=find_packages(),
    scripts=[('bin/%s' % f) for f in os.listdir(bindir)],
    data_files=[('/usr/share/sane/epjitsu',['ext/1300i_0D12.nal'])],
    zip_safe=False)
