import os
from setuptools import setup, find_packages


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name),
              encoding='utf-8') as file:
        return file.read()


setup(
    name='hynet',
    version='1.0.7',  # Update the version in __init__.py and conf.py as well
    author='Matthias Hotz',
    author_email='matthias.hotz@tum.de',
    description='An optimal power flow framework for hybrid AC/DC power systems.',
    long_description=read('README.md'),
    license='BSD 3-clause license',
    keywords='hybrid AC/DC power systems optimal power flow convex relaxation',
    url='http://www.msv.ei.tum.de/',
    packages=find_packages(exclude=['tests.*', 'tests', 'expansion']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: BSD License',
    ],
    python_requires='>=3.5',
    install_requires=[
        'sqlalchemy>=1.2.3',
        'numpy>=1.14.0',
        'scipy>=1.0.0',
        'pandas>=0.23.0',
        'matplotlib>=2.1.1',
        'h5py>=2.8.0'
    ],
    extras_require={
        'graph': ['networkx>=2.1'],
        'test': ['pytest>=3.5.0', 'pytest-cov', 'pylint>=1.8.4', 'pylint-exit',
                 'PICOS>=1.1.2', 'cvxopt>=1.2.1'],
        'doc': ['Sphinx>=1.7.8', 'sphinxcontrib-napoleon>=0.6.1',
                'numpydoc>=0.8.0', 'm2r>=0.1.14']
    }
)
