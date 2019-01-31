from setuptools import setup, find_packages

__VERSION__ = '0.1.1'

setup(
    name='rsutils_django',
    version=__VERSION__,
    description="A bunch of utilities for Django. Built with :heart: by Reckonsys ",  # NOQA
    long_description="BaseModels, Auth and others",
    url='https://github.com/reckonsys/rsutils_django',
    author='dhilipsiva',
    author_email='dhilipsiva@pm.me',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='rsutils reckonsys django',
    packages=find_packages(),
    entry_points='',
    install_requires=[
        'Django>=2.1.5',
        'django-safedelete==0.5.1',
        'django>2',

    ]
)
