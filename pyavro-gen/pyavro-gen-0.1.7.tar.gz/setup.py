"""
The setup configuration.
"""

from pathlib import Path

from setuptools import setup, find_packages

setup(
    name='pyavro-gen',
    version_format='{tag}',
    description='A typed class generator for Avro Schemata',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    keywords=['avro', 'classes', 'typing', 'types', 'type', 'typed', 'generation', 'creation',
              'schema', 'schemas', 'schemata'],
    url='https://gitlab.com/Jaumo/pyavro-gen',
    author='Jaumo GmbH',
    author_email='nicola.bova@jaumo.com',
    packages=find_packages(),
    scripts=[
        'pyavro_gen/pyavrogen.py',
        'pyavro_gen/pyavrogen_test.py'
    ],
    license='Apache2',
    install_requires=[
        'networkx==2.2',
        'pygments==2.2.0',
        'avro-python3',
        'pathlib',
        'factory_boy',
        'undictify>=0.6.2',
        'faker',
        'fastavro>=0.21.18',
        'isort',
        'avro-preprocessor>=0.0.50',
    ],
)
