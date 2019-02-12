import os
from setuptools import setup, find_packages

version = '0.1'

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst')) as fp:
    longdesc = fp.read()

# with open(os.path.join(here, 'CHANGELOG.rst')) as fp:
#     longdesc += "\n\n" + fp.read()


setup(
    name='ShopiCLI',
    version=version,
    packages=find_packages(),
    url='https://github.com/rshk/shopicli',
    license='BSD License',
    author='Samuele Santi',
    author_email='samuele.santi@reinventsoftware.io',
    description='Shopify command-line client',
    long_description=longdesc,
    install_requires=[
        'click >= 7',
        'requests >= 2',
        'nicelog >= 0.3',
        'pygments',
    ],
    # tests_require=tests_require,
    # test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: BSD License',

        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.0',
        # 'Programming Language :: Python :: 3.1',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',

        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        # 'Programming Language :: Python :: Implementation :: Stackless',
    ],
    entry_points={
        'console_scripts': ['shopicli=shopicli.cli:main'],
    },
    package_data={'': ['README.rst', 'CHANGELOG.rst']},
    include_package_data=True,
    zip_safe=False)
