#!/usr/bin/env python2

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GENIALbiologists",
    version="0.9.0",
    author="Pauline Barbet, Arnaud Felten",
    author_email="pauline.barbet@anses.fr, arnaud.felten@anses.fr",
    description="GENIAL: GENes Indentification with Abricate for Lucky biologists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/p-barbet/GENIAL",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
        scripts=['src/GENIAL',
             "src/GENIALanalysis",
             "src/GENIALresults",
             "src/GENIALmultidb",
             "src/update_databases",
             ],
    include_package_data = True,
    
    install_requires=['pandas',   
                      'seaborn',
                      'biopython',
                      ], # dependances dans PyPI

    dependency_links=['https://github.com/tseemann/abricate'], # depedances pas dans PyPI
    zip_safe=False,



)
