from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
#    name='aalto-boss',
    name='laos-boats',
    version='0.9.13',
#    description='Bayesian Optimization Structure Search',
    description='',
    long_description=long_description,
#    url='https://version.aalto.fi/gitlab/boss-devs/boss',
#    author=u'Ville Parkkinen, Henri Paulamaki, Milica Todorovic',
#    author_email='milica.todorovic@aalto.fi',
    license='BSD 3-clause',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
#        'Intended Audience :: Science/Research',
        'Intended Audience :: Customer Service',
#        'Topic :: Scientific/Engineering :: Physics',        
        'Topic :: Office/Business',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License'
    ],

    keywords='',
    packages=find_packages(),
    install_requires=[
        'GPy',
        'numpy',
        'scipy',
        'matplotlib'
    ],
    python_requires='~=3.5',
    entry_points={
        'console_scripts': [
            'boss=boss.__main__:main',
        ],
    },
)

