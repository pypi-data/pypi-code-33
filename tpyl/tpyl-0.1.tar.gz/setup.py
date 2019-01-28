import os
import re

from setuptools import setup


# Read required packages from requirements.txt file
requirements = 'requirements.txt'
reqs = []
if os.path.exists(requirements):
    with open(requirements, 'r') as f:
        reqs = [line.strip() for line in f if not re.match(r'^\s*#', line)]


# Fix toml: pkg_resources.ContextualVersionConflict
for i, val in enumerate(reqs):
    name, version = val.split('==')
    if name == 'toml':
        reqs[i] = name


setup(
    name='tpyl',
    packages=['tpyl'],
    py_modules=['tpyl', 'cli'],
    version='0.1',
    description='Simple template CLI using Jinja2.',
    long_description="""
Simple template CLI using Jinja2.

For more information visit:

https://gitlab.com/grautxo/tpyl
""",
    long_description_content_type="text/markdown",
    author='grautxo',
    url='https://gitlab.com/grautxo/tpyl',
    keywords=['template', 'cli'],
    install_requires=reqs,
    entry_points='''
        [console_scripts]
        tpyl=cli:cli
    ''',
)
