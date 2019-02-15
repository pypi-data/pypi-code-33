from setuptools import setup, find_namespace_packages
import unittest


def default_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


with open('LICENSE') as f:
    license_ = f.read()


with open('README.md') as f:
    readme = f.read()

setup(
    name='stika_patterns_observer',
    version='0.9',
    packages=find_namespace_packages(include=['stika.*']),
    url='https://github.com/KalleDK/stika-patterns-observer',
    license=license_,
    author='Kalle R. Møller',
    author_email='pypi@k-moeller.dk',
    description='Simple Observer Pattern',
    long_description=readme,
    zip_safe=False,
    install_requires=[
        'typing_extensions'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ],
    test_suite='setup.default_test_suite'
)
