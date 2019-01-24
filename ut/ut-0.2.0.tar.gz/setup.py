from setuptools import setup

entry_points = '''
[console_scripts]
ut=ut.cli:cli
'''

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ut',
    version='0.2.0',
    description='Universal Toolbox.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['ut'],
    entry_points=entry_points,
    install_requires=[
        'click',
    ],
)
