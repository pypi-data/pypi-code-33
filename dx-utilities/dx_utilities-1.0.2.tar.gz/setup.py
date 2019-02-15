from setuptools import setup, find_packages


long_description = """
# `dx-utilities` package

## Features

* Geometry module on top of `shapely`.
* Representations of physical fields.
* Linear algebra and numerical integration.

  * Utilities on top of `numpy` and `mathutils.Vector`.

* Decorators.
* Exception classes with error-code.
* Data-structures.
* Book-keeping of physical constants and manipulation of units.
* Testing and printing utilities.

### Sample usage

```
>>> from dx_utilities.geometry import PlanarShape
>>> rectangle = PlanarShape.new(shape='rectangle', bx=1.0, by=2.0)
>>> rectangle.area
2.0
```

## Public API

See the [documentation pages](https://d-e.gitlab.io/dx-utilities/).

## Contribute

Source code lives in https://gitlab.com/d-e/dx-utilities.
"""


setup(
    name='dx_utilities',
    packages=find_packages(exclude=['test*']),
    install_requires=[
        "sphinx>=1.8.3",
        "scipy>=1.1.0",
        "pyfarmhash>=0.2.2",
        "geos>=0.2.1",
        "nose2>=0.7.4",
        "shapely>=1.6.4.post1",
        "expiringdict==1.1.4",
        "mathutils==2.79.1"
        ],
    version='1.0.2',
    author="Konstantinos Demartinos",
    author_email="kostas@d-e.gr",
    maintainer="demetriou engineering ltd.",
    maintainer_email="kostas@d-e.gr",
    url="https://gitlab.com/d-e/dx-utilities",
    description="Base utilities for engineering packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        ("License :: OSI Approved :: GNU Affero General Public License "
         "v3 or later (AGPLv3+)"),
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        ],
    license='AGPLv3+'
    )
