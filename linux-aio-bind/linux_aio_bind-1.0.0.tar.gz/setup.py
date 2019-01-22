#!/usr/bin/env python
# coding: UTF-8

from setuptools import find_packages, setup

with open('README.md') as fp:
    readme = fp.read()

setup(
        name='linux_aio_bind',
        version='1.0.0',
        author='Byeonghoon Yoo',
        author_email='bh322yoo@gmail.com',
        description='Python binding for Linux AIO',
        long_description=readme,
        long_description_content_type='text/markdown',
        url='https://github.com/isac322/linux_aio_bind',
        packages=find_packages(exclude=('test',)),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: C',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: Implementation',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: Implementation :: Stackless',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System',
            'Topic :: System :: Filesystems',
            'Topic :: System :: Operating System',
            'Topic :: System :: Operating System Kernels',
            'Topic :: System :: Operating System Kernels :: Linux',
        ],
        license='LGPLv3+',
        keywords='Linux AIO ABI API binding file socket fd',
        python_requires='>=2.6',
        provides=['linux_aio_bind'],
        platforms='Linux',
        setup_requires=['cffi>=1.0.0'],
        install_requires=[
            'cffi>=1.0.0',
            'enum34;python_version<="3.3"'
        ],
        extras_require={
            'stub': ['typing']
        },
        cffi_modules=['linux_aio_bind/syscall.py:_ffibuilder'],
        package_data={
            'linux_aio_bind': ['*.pyi'],
        }
)
