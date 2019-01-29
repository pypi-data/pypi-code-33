from setuptools import setup, find_packages
import insightgis as gi

long_description = "InsightGIS: A single platform for enterprise architects to solve complex workflow and automation challenges without engaging engineering resources."

classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: GIS',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Physics',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]


# python setup.py sdist upload -r pypi
setup(
    name = 'insightgis',
    packages = find_packages(),
    install_requires=[],
    version = gi.__version__,
    description = 'Welcome to InsightGIS.',
    long_description=long_description,
    author = 'David Bernat',
    author_email = 'david@starlight.ai',
    url = '',
    classifiers=classifiers,
    keywords = ['satellite', 'imagery', 'remote sensing', "starlight", "platform", "gis"],
)