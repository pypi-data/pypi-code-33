from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='synopy',
    version='0.0.0',
    packages=['synopy'],
    url='https://github.com/graingert/synopy',
    license='MIT',
    author='George Spanos',
    author_email='spanosgeorge@gmail.com',
    maintainer='Thomas Grainger',
    maintainer_email='synopy@graingert.co.uk',
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='Python library for the Synology DiskStation APIs',
    install_requires=['requests>=2, <3.0.0'],
)
