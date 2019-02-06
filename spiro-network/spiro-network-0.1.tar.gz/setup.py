# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='spiro-network',
    version='0.1',
    description="Salt modules for discovering and exposing minion's IP addresses",  # Optional
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/spirostack/spiro-network',
    author='Jamie Bliss',
    author_email='jamie@ivyleav.es',
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        # 'Environment :: Salt',
        'Environment :: Other Environment',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU Affero General Public License v3',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='salt saltstack',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'vagrant']),  # Required
    install_requires=[
        'setuptools',  # For pkg_resources
        'requests',
    ],

    entry_points={
        'salt.loader': [
            '{0}_dirs=spiro_network.loader:{0}'.format(tag)
            for tag in (
                'auth', 'beacons', 'cache', 'engines', 'executor', 'fileserver',
                'grains', 'log_handlers', 'module', 'pillar', 'render',
                'returner', 'runner', 'serializers', 'states', 'tokens', 'top', 'utils',
                'wheel',
            )
        ],
    },
    zip_safe=False,
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/spirostack/spiro-network/issues',
        'Tip Jar': 'https://ko-fi.com/astraluma',
        'Source': 'https://gitlab.com/spirostack/spiro-network/',
    },
)
