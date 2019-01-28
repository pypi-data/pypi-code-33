import pathlib
from setuptools import setup

from amy import __name__, __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

setup(
    name=__name__,
    version=__version__,
    description='A module to write amy plugins',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/amy-assistant/plugins/python',
    author='Liam Perlaki',
    author_email='lperlaki@icloud.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['amy'],
    install_requires=['pika']
)
