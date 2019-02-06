import os

from setuptools import find_packages, setup

import versioneer


rootpath = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return open(os.path.join(rootpath, *parts), 'r').read()


long_description = f'{read("README.rst")}\n{read("CHANGES.txt")}'


with open('requirements.txt') as f:
    tests_require = f.readlines()
install_requires = [t.strip() for t in tests_require]


setup(
    name='ioos_tools',
    version=versioneer.get_version(),
    packages=find_packages(),
    cmdclass=versioneer.get_cmdclass(),
    license=f'{read("LICENSE.txt")}',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta'],
    description='Misc functions for IOOS notebooks',
    author=['Rich Signell', 'Filipe Fernandes'],
    author_email='ocefpaf@gmail.com',
    url='https://github.com/pyoceans/ioos_tools/releases',
    platforms='any',
    keywords=['oceanography', 'data analysis'],
    install_requires=install_requires,
    zip_safe=False,
)
