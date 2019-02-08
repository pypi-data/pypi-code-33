# -*- coding: utf-8 -*-

from setuptools import setup

short_description = \
    'Check usage STEPS subcellular simulator'


long_description = '{0}\n{1}'.format(
    open('README.rst').read(),
    open('CHANGES.rst').read(),
)

with open('LICENSE') as f:
    license = f.read()

setup(
    name='flake8-oist-steps',
    version='0.0.1.dev0',
    description=short_description,
    long_description=long_description,
    license=license,
    use_scm_version=True,
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
    ],
    keywords='pep8 flake8 python',
    author='Tristan Carel',
    author_email='tristan.carel@epfl.ch',
    url='https://github.com/tristan0x/flake8-oist-steps',
    py_modules=['flake8_oist_steps'],
    include_package_data=True,
    test_suite='run_tests',
    zip_safe=False,
    setup_requires=[
        'setuptools_scm==1.15.6',
    ],
    install_requires=[
        'flake8',
    ],
    extras_require={
        'test': [
            'coverage',
            'coveralls',
            'mock',
            'pytest',
            'pytest-cov',
        ],
    },
    entry_points={
        'flake8.extension': ['A00 = flake8_oist_steps:IdChecker'],
    },
)
