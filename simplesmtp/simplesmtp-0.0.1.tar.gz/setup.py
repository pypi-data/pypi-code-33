import os
import re
from setuptools import find_packages, setup

from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
]

tests_require = [
    'pytest'
]


def read_file(*parts):
    with open(os.path.join(here, *parts), 'r', encoding='utf-8') as fp:
        return fp.read()

def find_version(*paths):
    version_file = read_file(*paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


setup(
    name='simplesmtp',
    version=find_version('simplesmtp', '__init__.py'),
    description='A very simple class to send e-mails using the SMTP Python Lib',
    long_description=read_file('README.rst'),
    url='https://github.com/andidevel/simplesmtp',
    author='Anderson R. Livramento',
    author_email='andi.devel@gmail.com',
    license='Apache 2.0',
    packages=find_packages(exclude=['contrib', 'docs']),
    include_package_data=True,
    # install_requires=install_requires,
    extras_require={
        'testing': tests_require,
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
