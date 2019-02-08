#!/usr/bin/env python

from setuptools import find_packages, setup


version = '1.0'

setup(
    name='readyrector',
    packages=find_packages(),
    version=version,
    description='Easy to implement redirect middleware, which loads redirects '
                'from a configurable backend.',
    long_description=open('README.rst').read(),
    author='Sven Groot (Mediamoose)',
    author_email='sven@mediamoose.nl',
    url='https://gitlab.com/mediamoose/readyrector/tree/v{}'.format(version),  # noqa
    download_url='https://gitlab.com/mediamoose/readyrector/repository/v{}/archive.tar.gz'.format(version),  # noqa
    include_package_data=True,
    install_requires=[
        'django>=1.11',
    ],
    license='MIT',
    zip_safe=False,
    keywords=['redirect', 'middleware', 'django'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
