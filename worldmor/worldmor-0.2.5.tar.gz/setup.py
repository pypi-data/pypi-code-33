from setuptools import setup
from setuptools import find_packages
from distutils.core import Extension


class get_numpy_include(object):
    """Returns Numpy's include path with lazy import."""
    def __str__(self):
        import numpy
        return numpy.get_include()


with open('README.rst') as h_rst:
    LONG_DESCRIPTION = h_rst.read()
    LONG_DESCRIPTION = LONG_DESCRIPTION.replace('``', '$')  # protect existing code markers
    for xref in [':meth:', ':attr:', ':class:', ':func:']:
        LONG_DESCRIPTION = LONG_DESCRIPTION.replace(xref, '')  # remove xrefs
    LONG_DESCRIPTION = LONG_DESCRIPTION.replace('`', '``')  # replace refs with code markers
    LONG_DESCRIPTION = LONG_DESCRIPTION.replace('$', '``')  # restore existing code markers


module1 = Extension('worldmor.game.game', sources=['worldmor/game/game.pyx'])

setup(
    name='worldmor',
    license='GPLv3',
    version='0.2.5',
    description='Arcade 2D survival game.',
    long_description=LONG_DESCRIPTION,
    author='Ladislav Martínek',
    author_email='martilad@fit.cvut.cz',
    keywords='Worldmor, game, arcade, survival',
    url='https://github.com/martilad/worldmor',
    packages=find_packages(),
    ext_modules = [module1],
    include_package_data=True,
    include_dirs=[get_numpy_include()],
    install_requires=[
        'numpy>=1.12.0',
        'Cython',
        'Sphinx',
        'pytest',
        'PyQt5',
    ],
    setup_requires=[
        'Cython',
        'numpy>=1.12.0',
        'pytest-runner',
    ],
    entry_points={
        'console_scripts': [
            'worldmor = worldmor:main',
        ]
    },
    tests_require=[
        'pytest'
    ],
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Framework :: Pytest',
        'Framework :: Sphinx',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Topic :: Software Development',
        'Development Status :: 3 - Alpha',
        ],
    zip_safe=False,
)
