# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name='guillotina_pgcatalog',
    version='1.0.6',
    description='basic catalog implementation for guillotina on postgres',  # noqa
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGELOG.rst').read()),
    keywords=['asyncio', 'REST', 'Framework', 'transactional'],
    author='Nathan Van Gheem',
    author_email='vangheem@gmail.com',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    url='',
    license='private',
    setup_requires=[
        'pytest-runner',
    ],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'guillotina>=4.5.0'
    ],
    extras_require={
        'test': [
            'pytest',
            'requests',
            'docker',
            'backoff',
            'requests',
            'psycopg2',
            'pytest-asyncio',
            'pytest-aiohttp',
            'pytest-docker-fixtures'
        ]
    },
    entry_points={

    }
)
