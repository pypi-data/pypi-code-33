"""LIGO Synthetic PE

A Python library for rapidly generating synthetic parameter estimates (PE) for
compact binaries.
"""

from datetime import date


#-------------------------------------------------------------------------------
#   GENERAL
#-------------------------------------------------------------------------------
__name__        = "ligo_synthetic_pe"
__version__     = "2.0.0"
__date__        = date(2019, 1, 29)
__keywords__    = [
    "physics",
    "statistics",
]
__status__      = "Stable"


#-------------------------------------------------------------------------------
#   URLS
#-------------------------------------------------------------------------------
__url__         = "https://git.ligo.org/daniel.wysocki/synthetic-PE-posteriors"
__bugtrack_url__= "https://git.ligo.org/daniel.wysocki/synthetic-PE-posteriors/issues"


#-------------------------------------------------------------------------------
#   PEOPLE
#-------------------------------------------------------------------------------
__author__      = "Daniel Wysocki"
__author_email__= "daniel.wysocki@ligo.org"

__maintainer__      = "Daniel Wysocki"
__maintainer_email__= "daniel.wysocki@ligo.org"

__credits__     = ("Daniel Wysocki", "Richard O'Shaughnessy")


#-------------------------------------------------------------------------------
#   LEGAL
#-------------------------------------------------------------------------------
__copyright__   = 'Copyright (c) 2018-2019 {author} <{email}>'.format(
    author=__author__,
    email=__author_email__
)

__license__     = 'MIT'
__license_full__= '''
Licensed under MIT License
<https://opensource.org/licenses/MIT>
'''.strip()


#-------------------------------------------------------------------------------
#   PACKAGE
#-------------------------------------------------------------------------------
DOCLINES = __doc__.split("\n")

CLASSIFIERS = """
Development Status :: 3 - Alpha
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Operating System :: OS Independent
""".strip()

REQUIREMENTS = {
    "install": [
        "numpy>=1.13.0",
        "scipy>=1.0.0,<1.1.0",
        "six>=1.10.0,<1.11.0",
    ],
    "tests": [
    ]
}

ENTRYPOINTS = {
    "console_scripts" : [
        "ligo_synthetic_pe = ligo_synthetic_pe.cli:main",
    ]
}

from setuptools import find_packages, setup

metadata = dict(
    name        =__name__,
    version     =__version__,
    description =DOCLINES[0],
    long_description='\n'.join(DOCLINES[2:]),
    keywords    =__keywords__,

    author      =__author__,
    author_email=__author_email__,

    maintainer  =__maintainer__,
    maintainer_email=__maintainer_email__,

    url         =__url__,
#    download_url=__download_url__,

    license     =__license__,

    classifiers=[f for f in CLASSIFIERS.split('\n') if f],

    package_dir ={"": "src"},
    packages    =[
        "ligo_synthetic_pe",
        "ligo_synthetic_pe.EM_Bright",
    ],

    install_requires=REQUIREMENTS["install"],
#    tests_require=REQUIREMENTS["tests"],

    entry_points=ENTRYPOINTS
)

setup(**metadata)
