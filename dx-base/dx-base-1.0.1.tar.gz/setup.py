from setuptools import setup, find_packages

long_description = """
# `dx-base` package

A collection of base packages and modules for structural design software.

## Features

* Structural elements in plane.
* Exceptions with error-code.
* Nodal forces.
* Structural materials.
* Material safety factors.

### Sample usage

```
>>> from dx_base.safety_factors import SafetyFactor
>>> sf = SafetyFactor(1.24, 'persistent', 'serviceability')
>>> sf
1.24
>>> sf.design_situation
'persistent'
>>> sf.limit_stte
'serviceability'
```

## Contribute

Source code lives in https://gitlab.com/d-e/dx-base.

## Public API

See the [documentation pages](https://d-e.gitlab.io/dx-base/).
"""

setup(
    name='dx-base',
    packages=find_packages(exclude=['test*']),
    install_requires=[
        "dx-utilities>=1.0.0,<2.0.0",
        ],
    version='1.0.1',
    author="Konstantinos Demartinos",
    author_email="kostas@d-e.gr",
    maintainer="demetriou engineering ltd.",
    maintainer_email="kostas@d-e.gr",
    url="https://gitlab.com/d-e/dx-base",
    description="Base package for structural design software packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["structural-design", ],
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
