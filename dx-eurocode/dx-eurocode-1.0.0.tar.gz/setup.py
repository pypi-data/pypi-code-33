from setuptools import setup, find_packages

long_description = """
# `dx-eurocode`

A base package for structural design with [EN Eurocodes][EC].

## Features

* Eurocode, Part 0 ([EC0][])

  * Safety factors

* Eurocode, Part 2 ([EC2][])

  * Materials
  * Recurrent formulas
  * Safety factors

### Sample usage

```
>>> from dx_eurocode.EC2.materials import RC
>>> C16_20 = RC[16] # RC['16'] works as well!
>>> C16_20.fck
16000000.0
>>> C16_20.fcm
24000000.0
>>> C16_20.Ecm
28607904894.961403
>>> C16_20.gamma
{'accidental': {'ultimate': 1.2},
 'persistent': {'ultimate': 1.5},
 'transient': {'ultimate': 1.5}}
>>> C16_20.fcd(design_situation='persistent', limit_state='ultimate')
10666666.666666666
```

## Contribute

Source code lives in https://gitlab.com/d-e/dx-eurocode.

## Public API

See the [documentation pages](https://d-e.gitlab.io/dx-eurocode/).

[EC]: https://eurocodes.jrc.ec.europa.eu/
[EC0]: https://eurocodes.jrc.ec.europa.eu/showpage.php?id=130
[EC2]: https://eurocodes.jrc.ec.europa.eu/showpage.php?id=132
"""

setup(
    name='dx-eurocode',
    packages=find_packages(exclude=['test*']),
    install_requires=[
        "dx-base>=1.0.0,<2.0.0",
        ],
    version='1.0.0',
    author="Konstantinos Demartinos",
    author_email="kostas@d-e.gr",
    maintainer="demetriou engineering ltd.",
    maintainer_email="kostas@d-e.gr",
    url="https://gitlab.com/d-e/dx-eurocode",
    description="Base package for structural design with Eurocodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["structural-design", "eurocode"],
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
