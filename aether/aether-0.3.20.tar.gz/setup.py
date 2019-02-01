# python setup.py sdist bdist_wheel
# python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
# docker build -t gcr.io/aether-185123/minimum-user-docker-python27 -f minimum.user.docker.python27 .
# docker build -t gcr.io/aether-185123/minimum-user-docker-python37 -f minimum.user.docker.python37 .

from __future__ import absolute_import
from setuptools import setup, find_packages

REQUIRED_DEPENDENCIES = [
    "dill",
    "geocoder",
    "utm",
    "pyshp",
    "Pillow",
    "Shapely",
    "aenum",
    "numpy",
    "pyproj",
    "rasterio",
    "six",
    "tifffile",
    "geojson",
    "fiona",
    "tensorflow",
    "tensorboard",
    "oauth2client",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

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
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]


# python setup.py sdist upload -r pypi
setup(
    name = "aether",
    packages = find_packages(),
    install_requires=REQUIRED_DEPENDENCIES,
    version = "0.3.20",
    description = 'Welcome to the Aether Platform',
    long_description=long_description,
    author = 'David Bernat',
    author_email = 'david@starlight.ai',
    url = 'https://davidbernat.github.io/aether-user/html/index.html',
    classifiers=classifiers,
    keywords = ['satellite', 'imagery', 'remote sensing', "starlight", "platform", "gis"],
)