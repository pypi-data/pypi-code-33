
from setuptools import setup, find_packages

def read_file(name):
    with open(name) as fobj:
        return fobj.read().strip()

LONG_DESCRIPTION = read_file("README.md")
VERSION = read_file("config/VERSION")
REQUIREMENTS = read_file("config/requirements.txt").split('\n')
TEST_REQUIREMENTS = read_file("config/requirements-test.txt").split('\n')


setup(
    name='facsimile',
    version=VERSION,
    author='20C',
    author_email='code@20c.com',
    description='',
    long_description=LONG_DESCRIPTION,
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
    ],
    url='https://github.com/20c/facsimile',
    install_requires=REQUIREMENTS,
    test_requires=TEST_REQUIREMENTS,
    packages=find_packages(),
    package_data={'facsimile': ['script/*.sh']},
    scripts=['facsimile/bin/facs', 'facsimile/bin/version_bump_dev', 'facsimile/bin/version_merge_release'],
    zip_safe=False
)
