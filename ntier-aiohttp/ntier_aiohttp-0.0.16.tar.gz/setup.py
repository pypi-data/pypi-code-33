'''Setup for package.'''
import pathlib
from setuptools import (setup)

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
VERSION = '0.0.16'

setup(
    name='ntier_aiohttp',
    version=VERSION,
    description=(
        'Adapt N-Tier to aiohttp'
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author='Trey Cucco',
    author_email='fcucco@gmail.com',
    url='https://gitlab.com/tcucco/ntier-aiohttp',
    download_url='https://gitlab.com/tcucco/ntier-aiohttp/-/archive/master/ntier-aiohttp-master.tar.gz',
    package_data={'ntier_aiohttp': ['py.typed']},
    packages=['ntier_aiohttp'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    license='MIT',
    platforms='any',
    zip_safe=False,
    install_requires=[
        'aiohttp',
        'ntier>=0.0.17',
        'ujson',
        'webdi>=0.0.5',
    ],
)
